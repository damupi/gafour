from __future__ import annotations


class GA4CLIError(Exception):
    """Base error for all GA4 CLI errors.

    Attributes:
        message: Human-readable error description.
        hint: Optional contextual hint for the user.
        recovery_command: Optional CLI command the user can run to recover.
        exit_code: Process exit code to use when this error is caught.
    """

    exit_code: int = 1

    def __init__(
        self,
        message: str,
        hint: str | None = None,
        recovery_command: str | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.hint = hint
        self.recovery_command = recovery_command


class AuthError(GA4CLIError):
    """Raised when authentication fails or credentials are missing.

    Attributes:
        exit_code: Always 2 for auth errors.
    """

    exit_code: int = 2


class ValidationError(GA4CLIError):
    """Raised when input validation fails (invalid arguments, bad data).

    Attributes:
        exit_code: Always 3 for validation errors.
    """

    exit_code: int = 3


class ConfigError(GA4CLIError):
    """Raised when configuration is missing or malformed.

    Attributes:
        exit_code: Always 4 for config errors.
    """

    exit_code: int = 4


class NetworkError(GA4CLIError):
    """Raised when a network or transport-level failure occurs.

    Attributes:
        exit_code: Always 5 for network errors.
    """

    exit_code: int = 5


class PropertyNotFoundError(GA4CLIError):
    """Raised when the requested GA4 property does not exist or is not accessible.

    Args:
        property_id: The property ID that was not found.
    """

    exit_code: int = 1

    def __init__(self, property_id: str) -> None:
        super().__init__(
            message=f"Property '{property_id}' not found or not accessible.",
            hint="Ensure the property ID is correct and you have the required permissions.",
            recovery_command="ga4 properties list --account-id <account-id>",
        )
        self.property_id = property_id


class AccountNotFoundError(GA4CLIError):
    """Raised when the requested GA4 account does not exist or is not accessible.

    Args:
        account_id: The account ID that was not found.
    """

    exit_code: int = 1

    def __init__(self, account_id: str) -> None:
        super().__init__(
            message=f"Account '{account_id}' not found or not accessible.",
            hint="Ensure the account ID is correct and you have the required permissions.",
            recovery_command="ga4 accounts list",
        )
        self.account_id = account_id
