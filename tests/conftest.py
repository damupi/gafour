from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from typer.testing import CliRunner


@pytest.fixture()
def mock_admin_client() -> MagicMock:
    """A MagicMock replacing AnalyticsAdminServiceClient."""
    return MagicMock()


@pytest.fixture()
def mock_data_client() -> MagicMock:
    """A MagicMock replacing BetaAnalyticsDataClient."""
    return MagicMock()


@pytest.fixture()
def sample_account() -> MagicMock:
    """A mock proto account object with name='accounts/123'."""
    account = MagicMock()
    account.name = "accounts/123"
    account.display_name = "Test Account"
    account.region_code = "US"
    account.create_time = None
    account.update_time = None
    return account


@pytest.fixture()
def sample_property() -> MagicMock:
    """A mock proto property object with name='properties/456'."""
    prop = MagicMock()
    prop.name = "properties/456"
    prop.display_name = "Test Property"
    prop.time_zone = "America/New_York"
    prop.currency_code = "USD"
    prop.industry_category = None
    prop.create_time = None
    prop.update_time = None
    prop.parent = "accounts/123"
    return prop


@pytest.fixture()
def typer_runner() -> CliRunner:
    """A Typer CliRunner instance for invoking CLI commands in tests."""
    return CliRunner()
