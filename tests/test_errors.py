from __future__ import annotations

import pytest

from ga4x.errors import (
    AccountNotFoundError,
    AuthError,
    ConfigError,
    GA4CLIError,
    NetworkError,
    PropertyNotFoundError,
    ValidationError,
)


class TestGA4CLIError:
    def test_default_exit_code(self) -> None:
        err = GA4CLIError(message="Something went wrong")
        assert err.exit_code == 1

    def test_message_stored(self) -> None:
        err = GA4CLIError(message="test message")
        assert err.message == "test message"
        assert str(err) == "test message"

    def test_hint_stored(self) -> None:
        err = GA4CLIError(message="msg", hint="do this instead")
        assert err.hint == "do this instead"

    def test_recovery_command_stored(self) -> None:
        err = GA4CLIError(message="msg", recovery_command="ga4 fix")
        assert err.recovery_command == "ga4 fix"

    def test_no_hint_by_default(self) -> None:
        err = GA4CLIError(message="msg")
        assert err.hint is None

    def test_no_recovery_command_by_default(self) -> None:
        err = GA4CLIError(message="msg")
        assert err.recovery_command is None

    def test_is_exception(self) -> None:
        with pytest.raises(GA4CLIError):
            raise GA4CLIError(message="boom")


class TestAuthError:
    def test_exit_code_is_2(self) -> None:
        err = AuthError(message="auth failed")
        assert err.exit_code == 2

    def test_is_ga4_cli_error(self) -> None:
        err = AuthError(message="auth failed")
        assert isinstance(err, GA4CLIError)

    def test_message_and_hint(self) -> None:
        err = AuthError(message="bad token", hint="refresh it")
        assert err.message == "bad token"
        assert err.hint == "refresh it"


class TestValidationError:
    def test_exit_code_is_3(self) -> None:
        err = ValidationError(message="invalid input")
        assert err.exit_code == 3

    def test_is_ga4_cli_error(self) -> None:
        assert isinstance(ValidationError(message="x"), GA4CLIError)


class TestConfigError:
    def test_exit_code_is_4(self) -> None:
        err = ConfigError(message="bad config")
        assert err.exit_code == 4

    def test_is_ga4_cli_error(self) -> None:
        assert isinstance(ConfigError(message="x"), GA4CLIError)


class TestNetworkError:
    def test_exit_code_is_5(self) -> None:
        err = NetworkError(message="network failure")
        assert err.exit_code == 5

    def test_is_ga4_cli_error(self) -> None:
        assert isinstance(NetworkError(message="x"), GA4CLIError)


class TestPropertyNotFoundError:
    def test_exit_code_is_1(self) -> None:
        err = PropertyNotFoundError(property_id="123")
        assert err.exit_code == 1

    def test_message_contains_property_id(self) -> None:
        err = PropertyNotFoundError(property_id="456")
        assert "456" in err.message

    def test_hint_is_set(self) -> None:
        err = PropertyNotFoundError(property_id="123")
        assert err.hint is not None
        assert len(err.hint) > 0

    def test_recovery_command_is_set(self) -> None:
        err = PropertyNotFoundError(property_id="123")
        assert err.recovery_command is not None
        assert "ga4 properties list" in err.recovery_command

    def test_property_id_attribute(self) -> None:
        err = PropertyNotFoundError(property_id="789")
        assert err.property_id == "789"

    def test_is_ga4_cli_error(self) -> None:
        assert isinstance(PropertyNotFoundError(property_id="1"), GA4CLIError)


class TestAccountNotFoundError:
    def test_exit_code_is_1(self) -> None:
        err = AccountNotFoundError(account_id="123")
        assert err.exit_code == 1

    def test_message_contains_account_id(self) -> None:
        err = AccountNotFoundError(account_id="999")
        assert "999" in err.message

    def test_hint_is_set(self) -> None:
        err = AccountNotFoundError(account_id="123")
        assert err.hint is not None

    def test_recovery_command_is_set(self) -> None:
        err = AccountNotFoundError(account_id="123")
        assert err.recovery_command is not None
        assert "ga4 accounts list" in err.recovery_command

    def test_account_id_attribute(self) -> None:
        err = AccountNotFoundError(account_id="321")
        assert err.account_id == "321"

    def test_is_ga4_cli_error(self) -> None:
        assert isinstance(AccountNotFoundError(account_id="1"), GA4CLIError)
