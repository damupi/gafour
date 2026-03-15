from __future__ import annotations

from ga4x.config import Config
from ga4x.errors import AuthError


def build_data_client(config: Config) -> "BetaAnalyticsDataClient":  # type: ignore[name-defined]  # noqa: F821
    """Build a GA4 Data API client using the provided configuration.

    Args:
        config: Populated Config instance.

    Returns:
        Authenticated BetaAnalyticsDataClient.

    Raises:
        AuthError: If credentials are missing or authentication fails.
    """
    from google.analytics.data_v1beta import BetaAnalyticsDataClient  # type: ignore[import-untyped]

    try:
        if config.auth_method == "service-account":
            return _data_client_service_account(config)
        elif config.auth_method == "token":
            return _data_client_token(config)
        else:
            raise AuthError(
                message="OAuth2 authentication is not yet supported.",
                hint="Use 'service-account' or 'token' auth method instead.",
                recovery_command="ga4 auth login --method service-account",
            )
    except AuthError:
        raise
    except Exception as exc:
        raise AuthError(
            message=f"Failed to build Data API client: {exc}",
            hint="Check your credentials and network connection.",
            recovery_command="ga4 auth status",
        ) from exc


def build_admin_client(config: Config) -> "AnalyticsAdminServiceClient":  # type: ignore[name-defined]  # noqa: F821
    """Build a GA4 Admin API client using the provided configuration.

    Args:
        config: Populated Config instance.

    Returns:
        Authenticated AnalyticsAdminServiceClient.

    Raises:
        AuthError: If credentials are missing or authentication fails.
    """
    from google.analytics.admin_v1beta import AnalyticsAdminServiceClient  # type: ignore[import-untyped]

    try:
        if config.auth_method == "service-account":
            return _admin_client_service_account(config)
        elif config.auth_method == "token":
            return _admin_client_token(config)
        else:
            raise AuthError(
                message="OAuth2 authentication is not yet supported.",
                hint="Use 'service-account' or 'token' auth method instead.",
                recovery_command="ga4 auth login --method service-account",
            )
    except AuthError:
        raise
    except Exception as exc:
        raise AuthError(
            message=f"Failed to build Admin API client: {exc}",
            hint="Check your credentials and network connection.",
            recovery_command="ga4 auth status",
        ) from exc


def _data_client_service_account(config: Config) -> "BetaAnalyticsDataClient":  # type: ignore[name-defined]  # noqa: F821
    """Build Data API client with service account credentials."""
    from google.analytics.data_v1beta import BetaAnalyticsDataClient  # type: ignore[import-untyped]
    from google.oauth2 import service_account  # type: ignore[import-untyped]

    if not config.key_file:
        raise AuthError(
            message="No service account key file configured.",
            hint=(
                "Set GA4_KEY_FILE or GOOGLE_APPLICATION_CREDENTIALS environment variable, "
                "or run 'ga4 auth login --method service-account'."
            ),
            recovery_command="ga4 auth login --method service-account",
        )

    try:
        credentials = service_account.Credentials.from_service_account_file(
            config.key_file,
            scopes=["https://www.googleapis.com/auth/analytics.readonly"],
        )
        return BetaAnalyticsDataClient(credentials=credentials)
    except FileNotFoundError as exc:
        raise AuthError(
            message=f"Service account key file not found: {config.key_file}",
            hint="Verify the path is correct and the file exists.",
            recovery_command="ga4 config set key_file /path/to/service-account.json",
        ) from exc
    except Exception as exc:
        raise AuthError(
            message=f"Invalid service account key file: {exc}",
            hint="Ensure the JSON key file is valid and has the correct format.",
        ) from exc


def _data_client_token(config: Config) -> "BetaAnalyticsDataClient":  # type: ignore[name-defined]  # noqa: F821
    """Build Data API client with a bearer access token."""
    from google.analytics.data_v1beta import BetaAnalyticsDataClient  # type: ignore[import-untyped]
    from google.oauth2.credentials import Credentials  # type: ignore[import-untyped]

    if not config.access_token:
        raise AuthError(
            message="No access token configured.",
            hint="Set GA4_ACCESS_TOKEN environment variable or run 'ga4 auth login --method token'.",
            recovery_command="ga4 auth login --method token",
        )

    quota_project = _adc_quota_project()
    credentials = Credentials(
        token=config.access_token,
        quota_project_id=quota_project,
    )
    return BetaAnalyticsDataClient(credentials=credentials)


def _admin_client_service_account(config: Config) -> "AnalyticsAdminServiceClient":  # type: ignore[name-defined]  # noqa: F821
    """Build Admin API client with service account credentials."""
    from google.analytics.admin_v1beta import AnalyticsAdminServiceClient  # type: ignore[import-untyped]
    from google.oauth2 import service_account  # type: ignore[import-untyped]

    if not config.key_file:
        raise AuthError(
            message="No service account key file configured.",
            hint=(
                "Set GA4_KEY_FILE or GOOGLE_APPLICATION_CREDENTIALS environment variable, "
                "or run 'ga4 auth login --method service-account'."
            ),
            recovery_command="ga4 auth login --method service-account",
        )

    try:
        credentials = service_account.Credentials.from_service_account_file(
            config.key_file,
            scopes=["https://www.googleapis.com/auth/analytics.readonly"],
        )
        return AnalyticsAdminServiceClient(credentials=credentials)
    except FileNotFoundError as exc:
        raise AuthError(
            message=f"Service account key file not found: {config.key_file}",
            hint="Verify the path is correct and the file exists.",
            recovery_command="ga4 config set key_file /path/to/service-account.json",
        ) from exc
    except Exception as exc:
        raise AuthError(
            message=f"Invalid service account key file: {exc}",
            hint="Ensure the JSON key file is valid and has the correct format.",
        ) from exc


def _admin_client_token(config: Config) -> "AnalyticsAdminServiceClient":  # type: ignore[name-defined]  # noqa: F821
    """Build Admin API client with a bearer access token."""
    from google.analytics.admin_v1beta import AnalyticsAdminServiceClient  # type: ignore[import-untyped]
    from google.oauth2.credentials import Credentials  # type: ignore[import-untyped]

    if not config.access_token:
        raise AuthError(
            message="No access token configured.",
            hint="Set GA4_ACCESS_TOKEN environment variable or run 'ga4 auth login --method token'.",
            recovery_command="ga4 auth login --method token",
        )

    quota_project = _adc_quota_project()
    credentials = Credentials(
        token=config.access_token,
        quota_project_id=quota_project,
    )
    return AnalyticsAdminServiceClient(credentials=credentials)


def _adc_quota_project() -> str | None:
    """Read the quota_project_id from the Application Default Credentials file.

    When authenticating with user OAuth2 credentials, Google APIs require a
    billing/quota project to be specified. ``gcloud auth application-default
    login`` writes this into the ADC JSON file automatically.

    Returns:
        The quota project ID string, or ``None`` if not available.
    """
    import json
    from pathlib import Path

    adc_path = Path.home() / ".config" / "gcloud" / "application_default_credentials.json"
    try:
        data = json.loads(adc_path.read_text(encoding="utf-8"))
        return data.get("quota_project_id")
    except (OSError, json.JSONDecodeError):
        return None
