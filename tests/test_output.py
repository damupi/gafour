from __future__ import annotations

import csv
import io
import json

import pytest

from gafour.output import OutputFormat, render


SAMPLE_DATA = [
    {"Name": "Alice", "Score": "95", "City": "New York"},
    {"Name": "Bob", "Score": "87", "City": "London"},
]

COLUMNS = ["Name", "Score", "City"]


class TestRenderTable:
    def test_contains_column_headers(self) -> None:
        result = render(SAMPLE_DATA, OutputFormat.TABLE, COLUMNS)
        assert "Name" in result
        assert "Score" in result
        assert "City" in result

    def test_contains_row_data(self) -> None:
        result = render(SAMPLE_DATA, OutputFormat.TABLE, COLUMNS)
        assert "Alice" in result
        assert "Bob" in result
        assert "95" in result
        assert "87" in result
        assert "New York" in result

    def test_empty_data_returns_no_results(self) -> None:
        result = render([], OutputFormat.TABLE, COLUMNS)
        assert "(no results)" in result

    def test_uses_dict_keys_when_no_columns(self) -> None:
        result = render(SAMPLE_DATA, OutputFormat.TABLE)
        assert "Name" in result
        assert "Score" in result


class TestRenderJSON:
    def test_valid_json(self) -> None:
        result = render(SAMPLE_DATA, OutputFormat.JSON, COLUMNS)
        parsed = json.loads(result)
        assert isinstance(parsed, list)

    def test_contains_expected_keys(self) -> None:
        result = render(SAMPLE_DATA, OutputFormat.JSON, COLUMNS)
        parsed = json.loads(result)
        assert parsed[0]["Name"] == "Alice"
        assert parsed[1]["Name"] == "Bob"

    def test_contains_expected_values(self) -> None:
        result = render(SAMPLE_DATA, OutputFormat.JSON, COLUMNS)
        parsed = json.loads(result)
        assert parsed[0]["Score"] == "95"
        assert parsed[1]["City"] == "London"

    def test_empty_data_returns_empty_array(self) -> None:
        result = render([], OutputFormat.JSON, COLUMNS)
        assert result == "[]"

    def test_indented_output(self) -> None:
        result = render(SAMPLE_DATA, OutputFormat.JSON, COLUMNS)
        # Verify indented (pretty-printed) JSON
        assert "\n" in result


class TestRenderCSV:
    def test_first_line_is_headers(self) -> None:
        result = render(SAMPLE_DATA, OutputFormat.CSV, COLUMNS)
        lines = result.strip().splitlines()
        assert lines[0] == "Name,Score,City"

    def test_second_line_is_first_row(self) -> None:
        result = render(SAMPLE_DATA, OutputFormat.CSV, COLUMNS)
        lines = result.strip().splitlines()
        assert "Alice" in lines[1]
        assert "95" in lines[1]

    def test_all_rows_present(self) -> None:
        result = render(SAMPLE_DATA, OutputFormat.CSV, COLUMNS)
        lines = result.strip().splitlines()
        # header + 2 data rows
        assert len(lines) == 3

    def test_parseable_by_csv_reader(self) -> None:
        result = render(SAMPLE_DATA, OutputFormat.CSV, COLUMNS)
        reader = csv.DictReader(io.StringIO(result))
        rows = list(reader)
        assert len(rows) == 2
        assert rows[0]["Name"] == "Alice"
        assert rows[1]["Name"] == "Bob"

    def test_empty_data_returns_empty_string(self) -> None:
        result = render([], OutputFormat.CSV, COLUMNS)
        assert result == ""

    def test_column_filtering(self) -> None:
        result = render(SAMPLE_DATA, OutputFormat.CSV, ["Name", "Score"])
        reader = csv.DictReader(io.StringIO(result))
        rows = list(reader)
        assert "City" not in rows[0]
        assert "Name" in rows[0]
