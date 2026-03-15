"""Tests for the filter expression DSL parser (ga4.filters)."""

from __future__ import annotations

import pytest

from ga4x.filters import parse_filter_expression
from ga4x.models.report import FilterExpression, FilterField, NumericFilter, StringFilter


# ---------------------------------------------------------------------------
# Simple comparisons
# ---------------------------------------------------------------------------


def test_exact_string_filter() -> None:
    fe = parse_filter_expression('country = "Spain"')
    assert fe.filter is not None
    assert fe.filter.field_name == "country"
    assert fe.filter.string_filter == StringFilter(match_type="EXACT", value="Spain")


def test_begins_with_filter() -> None:
    fe = parse_filter_expression('pagePath beginsWith "/"')
    assert fe.filter is not None
    assert fe.filter.field_name == "pagePath"
    assert fe.filter.string_filter is not None
    assert fe.filter.string_filter.match_type == "BEGINS_WITH"
    assert fe.filter.string_filter.value == "/"


def test_ends_with_filter() -> None:
    fe = parse_filter_expression('pagePath endsWith ".html"')
    assert fe.filter is not None
    assert fe.filter.string_filter is not None
    assert fe.filter.string_filter.match_type == "ENDS_WITH"


def test_contains_filter() -> None:
    fe = parse_filter_expression('pageTitle contains "Home"')
    assert fe.filter is not None
    assert fe.filter.string_filter is not None
    assert fe.filter.string_filter.match_type == "CONTAINS"


def test_matches_filter() -> None:
    fe = parse_filter_expression('pagePath matches "^/blog/.*"')
    assert fe.filter is not None
    assert fe.filter.string_filter is not None
    assert fe.filter.string_filter.match_type == "FULL_REGEXP"
    assert fe.filter.string_filter.value == "^/blog/.*"


def test_not_equal_string_filter() -> None:
    fe = parse_filter_expression('deviceCategory != "tablet"')
    assert fe.not_expression is not None
    inner = fe.not_expression
    assert inner.filter is not None
    assert inner.filter.field_name == "deviceCategory"
    assert inner.filter.string_filter is not None
    assert inner.filter.string_filter.match_type == "EXACT"
    assert inner.filter.string_filter.value == "tablet"


# ---------------------------------------------------------------------------
# Numeric comparisons
# ---------------------------------------------------------------------------


def test_numeric_greater_than() -> None:
    fe = parse_filter_expression("sessions > 100")
    assert fe.filter is not None
    assert fe.filter.field_name == "sessions"
    assert fe.filter.numeric_filter is not None
    assert fe.filter.numeric_filter.operation == "GREATER_THAN"
    assert fe.filter.numeric_filter.value.double_value == 100.0


def test_numeric_less_than_or_equal() -> None:
    fe = parse_filter_expression("bounceRate <= 0.5")
    assert fe.filter is not None
    assert fe.filter.numeric_filter is not None
    assert fe.filter.numeric_filter.operation == "LESS_THAN_OR_EQUAL"
    assert fe.filter.numeric_filter.value.double_value == 0.5


def test_numeric_equal() -> None:
    fe = parse_filter_expression("eventCount = 1")
    assert fe.filter is not None
    assert fe.filter.numeric_filter is not None
    assert fe.filter.numeric_filter.operation == "EQUAL"


def test_numeric_not_equal() -> None:
    fe = parse_filter_expression("sessions != 0")
    assert fe.not_expression is not None
    inner = fe.not_expression
    assert inner.filter is not None
    assert inner.filter.field_name == "sessions"
    assert inner.filter.numeric_filter is not None
    assert inner.filter.numeric_filter.operation == "EQUAL"


# ---------------------------------------------------------------------------
# NOT
# ---------------------------------------------------------------------------


def test_not_expression() -> None:
    fe = parse_filter_expression('NOT deviceCategory = "tablet"')
    assert fe.not_expression is not None
    inner = fe.not_expression
    assert inner.filter is not None
    assert inner.filter.field_name == "deviceCategory"


# ---------------------------------------------------------------------------
# AND
# ---------------------------------------------------------------------------


def test_and_two_filters() -> None:
    fe = parse_filter_expression('country = "Spain" AND NOT deviceCategory = "tablet"')
    assert fe.and_group is not None
    assert len(fe.and_group) == 2
    assert fe.and_group[0].filter is not None
    assert fe.and_group[0].filter.field_name == "country"
    assert fe.and_group[1].not_expression is not None


def test_and_three_filters() -> None:
    fe = parse_filter_expression(
        'pagePath beginsWith "/" AND country = "Spain" AND NOT deviceCategory = "tablet"'
    )
    assert fe.and_group is not None
    assert len(fe.and_group) == 3
    assert fe.and_group[0].filter is not None
    assert fe.and_group[0].filter.field_name == "pagePath"
    assert fe.and_group[1].filter is not None
    assert fe.and_group[1].filter.field_name == "country"
    assert fe.and_group[2].not_expression is not None


# ---------------------------------------------------------------------------
# OR
# ---------------------------------------------------------------------------


def test_or_two_filters() -> None:
    fe = parse_filter_expression('sessionSource = "google" OR sessionSource = "bing"')
    assert fe.or_group is not None
    assert len(fe.or_group) == 2
    assert fe.or_group[0].filter is not None
    assert fe.or_group[0].filter.string_filter is not None
    assert fe.or_group[0].filter.string_filter.value == "google"
    assert fe.or_group[1].filter is not None
    assert fe.or_group[1].filter.string_filter is not None
    assert fe.or_group[1].filter.string_filter.value == "bing"


# ---------------------------------------------------------------------------
# Operator precedence: AND binds tighter than OR
# ---------------------------------------------------------------------------


def test_and_over_or_precedence() -> None:
    # "A OR B AND C" should parse as "A OR (B AND C)"
    fe = parse_filter_expression(
        'country = "Spain" OR country = "France" AND NOT deviceCategory = "tablet"'
    )
    assert fe.or_group is not None
    assert len(fe.or_group) == 2
    # left: country = "Spain"
    assert fe.or_group[0].filter is not None
    assert fe.or_group[0].filter.field_name == "country"
    # right: country = "France" AND NOT ...
    assert fe.or_group[1].and_group is not None


# ---------------------------------------------------------------------------
# Grouping
# ---------------------------------------------------------------------------


def test_grouping_changes_precedence() -> None:
    # "(A OR B) AND C"
    fe = parse_filter_expression(
        '(country = "Spain" OR country = "France") AND sessions > 100'
    )
    assert fe.and_group is not None
    assert len(fe.and_group) == 2
    assert fe.and_group[0].or_group is not None
    assert fe.and_group[1].filter is not None
    assert fe.and_group[1].filter.field_name == "sessions"


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------


def test_empty_expression_raises() -> None:
    with pytest.raises(ValueError, match="empty"):
        parse_filter_expression("")


def test_missing_value_raises() -> None:
    with pytest.raises(ValueError):
        parse_filter_expression("country =")


def test_unknown_operator_raises() -> None:
    with pytest.raises(ValueError):
        parse_filter_expression('country ~= "Spain"')


def test_unmatched_paren_raises() -> None:
    with pytest.raises(ValueError):
        parse_filter_expression('(country = "Spain"')


def test_extra_token_raises() -> None:
    with pytest.raises(ValueError, match="Unexpected token"):
        parse_filter_expression('country = "Spain" "extra"')
