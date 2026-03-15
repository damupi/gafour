"""Filter expression DSL parser for GA4 Data API FilterExpression protos.

``parse_filter_expression`` converts a human-readable DSL string into a
``FilterExpression`` Pydantic model (defined in ``ga4.models.report``).

``filter_expression_to_proto`` converts that model to the
``google.analytics.data_v1beta.types.FilterExpression`` proto required by the
GA4 Data API client.

Syntax
------
  comparison  ::= fieldName op value
  op          ::= '=' | '!=' | 'beginsWith' | 'endsWith' | 'contains' | 'matches'
                | '<' | '<=' | '>' | '>='
  value       ::= '"..."' | "'...'" | number
  atom        ::= comparison | NOT atom | '(' expr ')'
  and_expr    ::= atom (AND atom)*
  expr        ::= and_expr (OR and_expr)*

Examples
--------
  pagePath beginsWith "/"
  country = "Spain" AND NOT deviceCategory = "tablet"
  sessionSource = "google" OR sessionSource = "bing"
  (country = "Spain" OR country = "France") AND sessions > 100
  pagePath beginsWith "/" AND country = "Spain" AND NOT deviceCategory = "tablet"
"""

from __future__ import annotations

import re

from gafour.models.report import (
    FilterExpression,
    FilterField,
    NumericFilter,
    NumericValue,
    StringFilter,
)

# ---------------------------------------------------------------------------
# Tokenizer
# ---------------------------------------------------------------------------

_TOKEN_RE = re.compile(
    r"""
    (?P<STRING>  "(?:[^"\\]|\\.)*"  |  '(?:[^'\\]|\\.)*' )  # quoted strings
  | (?P<NUMBER>  -?\d+(?:\.\d+)? )                           # numeric literals
  | (?P<OP>     !=|<=|>=|<|>|= )                             # symbolic operators
  | (?P<WORD>   [A-Za-z_][A-Za-z0-9_]* )                     # identifiers / keywords
  | (?P<LPAREN> \( )
  | (?P<RPAREN> \) )
  | (?P<SKIP>   \s+ )
    """,
    re.VERBOSE,
)

_KEYWORDS_AND = frozenset({"AND"})
_KEYWORDS_OR = frozenset({"OR"})
_KEYWORDS_NOT = frozenset({"NOT"})

_STRING_MATCH_TYPES: dict[str, str] = {
    "=": "EXACT",
    "beginsWith": "BEGINS_WITH",
    "endsWith": "ENDS_WITH",
    "contains": "CONTAINS",
    "matches": "FULL_REGEXP",
}

_NUMERIC_OPERATIONS: dict[str, str] = {
    "=": "EQUAL",
    "<": "LESS_THAN",
    "<=": "LESS_THAN_OR_EQUAL",
    ">": "GREATER_THAN",
    ">=": "GREATER_THAN_OR_EQUAL",
}


def _tokenize(text: str) -> list[tuple[str, str]]:
    tokens: list[tuple[str, str]] = []
    cursor = 0
    for m in _TOKEN_RE.finditer(text):
        if m.start() > cursor:
            raise ValueError(
                f"Unrecognized character(s) in filter expression at position {cursor}: "
                f"{text[cursor:m.start()]!r}"
            )
        kind = m.lastgroup
        if kind != "SKIP":
            tokens.append((kind, m.group()))  # type: ignore[arg-type]
        cursor = m.end()
    if cursor < len(text):
        raise ValueError(
            f"Unrecognized character(s) in filter expression at position {cursor}: "
            f"{text[cursor:]!r}"
        )
    return tokens


# ---------------------------------------------------------------------------
# Recursive-descent parser
# ---------------------------------------------------------------------------


class _Parser:
    def __init__(self, tokens: list[tuple[str, str]]) -> None:
        self._tokens = tokens
        self._pos = 0

    # -- helpers -------------------------------------------------------------

    def _peek(self) -> tuple[str, str] | None:
        return self._tokens[self._pos] if self._pos < len(self._tokens) else None

    def _consume(self) -> tuple[str, str]:
        tok = self._tokens[self._pos]
        self._pos += 1
        return tok

    def _expect(self, kind: str) -> tuple[str, str]:
        tok = self._peek()
        if tok is None or tok[0] != kind:
            raise ValueError(f"Expected {kind}, got {tok!r}")
        return self._consume()

    def _is_keyword(self, kw_set: frozenset[str]) -> bool:
        tok = self._peek()
        return tok is not None and tok[0] == "WORD" and tok[1].upper() in kw_set

    # -- grammar rules -------------------------------------------------------

    def parse(self) -> FilterExpression:
        expr = self._parse_or()
        if self._peek() is not None:
            raise ValueError(f"Unexpected token at end: {self._peek()!r}")
        return expr

    def _parse_or(self) -> FilterExpression:
        exprs = [self._parse_and()]
        while self._is_keyword(_KEYWORDS_OR):
            self._consume()
            exprs.append(self._parse_and())
        if len(exprs) == 1:
            return exprs[0]
        return FilterExpression(or_group=exprs)

    def _parse_and(self) -> FilterExpression:
        exprs = [self._parse_not()]
        while self._is_keyword(_KEYWORDS_AND):
            self._consume()
            exprs.append(self._parse_not())
        if len(exprs) == 1:
            return exprs[0]
        return FilterExpression(and_group=exprs)

    def _parse_not(self) -> FilterExpression:
        if self._is_keyword(_KEYWORDS_NOT):
            self._consume()
            inner = self._parse_atom()
            return FilterExpression(not_expression=inner)
        return self._parse_atom()

    def _parse_atom(self) -> FilterExpression:
        tok = self._peek()
        if tok and tok[0] == "LPAREN":
            self._consume()
            expr = self._parse_or()
            self._expect("RPAREN")
            return expr
        return self._parse_comparison()

    def _parse_comparison(self) -> FilterExpression:
        # field
        field_tok = self._peek()
        if not field_tok or field_tok[0] != "WORD":
            raise ValueError(f"Expected field name, got {field_tok!r}")
        if field_tok[1].upper() in _KEYWORDS_AND | _KEYWORDS_OR | _KEYWORDS_NOT:
            raise ValueError(
                f"Keyword {field_tok[1]!r} cannot be used as a field name."
            )
        field_name = self._consume()[1]

        # operator
        op_tok = self._peek()
        if not op_tok or op_tok[0] not in ("OP", "WORD"):
            raise ValueError(f"Expected operator after field name {field_name!r}, got {op_tok!r}")
        op = self._consume()[1]

        # value
        value_tok = self._peek()
        if not value_tok:
            raise ValueError(f"Expected value after operator {op!r}")

        if value_tok[0] == "STRING":
            raw = self._consume()[1]
            value_str = raw[1:-1].replace('\\"', '"').replace("\\'", "'")
            return self._build_string_filter(field_name, op, value_str)

        if value_tok[0] == "NUMBER":
            raw = self._consume()[1]
            return self._build_numeric_filter(field_name, op, float(raw))

        raise ValueError(
            f"Expected string or number value after {field_name!r} {op!r}, got {value_tok!r}"
        )

    # -- filter builders (return Pydantic models) ----------------------------

    def _build_string_filter(self, field_name: str, op: str, value: str) -> FilterExpression:
        if op == "!=":
            return FilterExpression(
                not_expression=FilterExpression(
                    filter=FilterField(
                        field_name=field_name,
                        string_filter=StringFilter(match_type="EXACT", value=value),
                    )
                )
            )
        match_type = _STRING_MATCH_TYPES.get(op)
        if match_type is None:
            raise ValueError(f"Unknown string operator: {op!r}")
        return FilterExpression(
            filter=FilterField(
                field_name=field_name,
                string_filter=StringFilter(match_type=match_type, value=value),
            )
        )

    def _build_numeric_filter(self, field_name: str, op: str, value: float) -> FilterExpression:
        if op == "!=":
            return FilterExpression(
                not_expression=FilterExpression(
                    filter=FilterField(
                        field_name=field_name,
                        numeric_filter=NumericFilter(
                            operation="EQUAL", value=NumericValue(double_value=value)
                        ),
                    )
                )
            )
        operation = _NUMERIC_OPERATIONS.get(op)
        if operation is None:
            raise ValueError(f"Unknown numeric operator: {op!r}")
        return FilterExpression(
            filter=FilterField(
                field_name=field_name,
                numeric_filter=NumericFilter(
                    operation=operation, value=NumericValue(double_value=value)
                ),
            )
        )


# ---------------------------------------------------------------------------
# Public API: parsing
# ---------------------------------------------------------------------------


def parse_filter_expression(expr_str: str) -> FilterExpression:
    """Parse a filter DSL string into a ``FilterExpression`` Pydantic model.

    Supported operators
    -------------------
    String fields:
      ``=``            exact match (case-insensitive)
      ``!=``           not exact match
      ``beginsWith``   begins with prefix
      ``endsWith``     ends with suffix
      ``contains``     substring match
      ``matches``      full regular expression

    Numeric fields:
      ``=``  ``!=``  ``<``  ``<=``  ``>``  ``>=``

    Connectives (AND binds tighter than OR):
      ``AND``   conjunction
      ``OR``    disjunction
      ``NOT``   negation (prefix)
      ``(...)`` grouping

    Examples
    --------
    ::

        pagePath beginsWith "/"
        country = "Spain" AND NOT deviceCategory = "tablet"
        sessionSource = "google" OR sessionSource = "bing"
        (country = "Spain" OR country = "France") AND sessions > 100
        pagePath beginsWith "/" AND country = "Spain" AND NOT deviceCategory = "tablet"

    Raises
    ------
    ValueError
        If the expression cannot be parsed.
    """
    tokens = _tokenize(expr_str.strip())
    if not tokens:
        raise ValueError("Filter expression must not be empty.")
    return _Parser(tokens).parse()


# ---------------------------------------------------------------------------
# Public API: proto conversion
# ---------------------------------------------------------------------------


def filter_expression_to_proto(fe: FilterExpression) -> object:
    """Convert a ``FilterExpression`` Pydantic model to a GA4 proto.

    Returns a ``google.analytics.data_v1beta.types.FilterExpression`` instance
    ready to pass to ``RunReportRequest.dimension_filter`` or
    ``RunReportRequest.metric_filter``.
    """
    from google.analytics.data_v1beta.types import (  # type: ignore[import-untyped]
        Filter,
        FilterExpression as ProtoFilterExpression,
        FilterExpressionList,
        NumericValue as ProtoNumericValue,
    )

    if fe.and_group is not None:
        return ProtoFilterExpression(
            and_group=FilterExpressionList(
                expressions=[filter_expression_to_proto(e) for e in fe.and_group]
            )
        )

    if fe.or_group is not None:
        return ProtoFilterExpression(
            or_group=FilterExpressionList(
                expressions=[filter_expression_to_proto(e) for e in fe.or_group]
            )
        )

    if fe.not_expression is not None:
        return ProtoFilterExpression(
            not_expression=filter_expression_to_proto(fe.not_expression)
        )

    if fe.filter is not None:
        f = fe.filter
        if f.string_filter is not None:
            sf = f.string_filter
            match_type = Filter.StringFilter.MatchType[sf.match_type]
            return ProtoFilterExpression(
                filter=Filter(
                    field_name=f.field_name,
                    string_filter=Filter.StringFilter(
                        match_type=match_type,
                        value=sf.value,
                        case_sensitive=sf.case_sensitive,
                    ),
                )
            )
        if f.numeric_filter is not None:
            nf = f.numeric_filter
            operation = Filter.NumericFilter.Operation[nf.operation]
            return ProtoFilterExpression(
                filter=Filter(
                    field_name=f.field_name,
                    numeric_filter=Filter.NumericFilter(
                        operation=operation,
                        value=ProtoNumericValue(double_value=nf.value.double_value),
                    ),
                )
            )

    raise ValueError(f"FilterExpression has no recognized field set: {fe!r}")
