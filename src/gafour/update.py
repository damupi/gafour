"""Bounded GitHub release checks and safe self-upgrades for gafour."""

from __future__ import annotations

import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from collections.abc import Callable, Mapping
from importlib import metadata
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

from gafour.config import CONFIG_PATH

REPO = "damupi/gafour"
REPO_GIT_HTTPS = f"https://github.com/{REPO}.git"
REPO_INSTALL_HTTPS = f"git+https://github.com/{REPO}"
RELEASE_API = f"https://api.github.com/repos/{REPO}/releases/latest"
RELEASE_URL = f"https://github.com/{REPO}/releases/tag"
CACHE_NAME = "update-check.json"
CHECK_INTERVAL = 24 * 3600
DISABLE_ENV = "GAFOUR_NO_UPDATE_CHECK"

_TAG_REF = re.compile(r"refs/tags/v(\d+)\.(\d+)\.(\d+)$")
_RELEASE_TAG = re.compile(r"^v(\d+)\.(\d+)\.(\d+)$")
_VERSION = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")

_UNSAFE_GIT_ENV = (
    "GIT_ASKPASS",
    "SSH_ASKPASS",
    "GIT_ASKPASS_REQUIRE",
    "GIT_CREDENTIAL_HELPER",
    "GIT_CONFIG",
    "GIT_CONFIG_GLOBAL",
    "GIT_CONFIG_SYSTEM",
    "GIT_CONFIG_PARAMETERS",
    "GIT_DIR",
    "GIT_WORK_TREE",
    "GIT_COMMON_DIR",
    "GIT_INDEX_FILE",
    "GIT_OBJECT_DIRECTORY",
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_SSH",
    "GIT_SSH_COMMAND",
    "GIT_SSH_VARIANT",
)
_GIT_CONFIG = (
    ("credential.helper", ""),
    ("credential.https://github.com.helper", ""),
    ("credential.interactive", "false"),
    ("core.askPass", ""),
    ("http.extraHeader", ""),
    ("http.https://github.com/.extraHeader", ""),
)


class UpgradeError(RuntimeError):
    """Raised when an upgrade cannot start or exits unsuccessfully."""


def config_dir() -> Path:
    override = os.environ.get("GAFOUR_CONFIG_DIR")
    return Path(override).expanduser() if override else CONFIG_PATH.parent


def cache_path() -> Path:
    return config_dir() / CACHE_NAME


def _write_private(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent, text=True)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
        os.replace(temporary, path)
        os.chmod(path, 0o600)
    except Exception:
        try:
            os.close(fd)
        except OSError:
            pass
        Path(temporary).unlink(missing_ok=True)
        raise


def _version_tuple(value: str | None) -> tuple[int, int, int] | None:
    match = _VERSION.fullmatch(value or "")
    if match is None:
        return None
    major, minor, patch = map(int, match.groups())
    return major, minor, patch


def is_newer(latest: str | None, current: str | None) -> bool:
    latest_tuple = _version_tuple(latest)
    current_tuple = _version_tuple(current)
    return latest_tuple is not None and current_tuple is not None and latest_tuple > current_tuple


def _curl_argv(timeout: float) -> list[str] | None:
    executable = shutil.which("curl")
    if executable is None:
        return None
    return [
        executable,
        "--disable",
        "--fail",
        "--silent",
        "--show-error",
        "--location",
        "--proto",
        "=https",
        "--max-time",
        f"{max(timeout, 0.01):.3f}",
        "--header",
        "Accept: application/vnd.github+json",
        "--header",
        "User-Agent: gafour-update-check",
        RELEASE_API,
    ]


def latest_release_api(timeout: float) -> str | None:
    if timeout <= 0 or (argv := _curl_argv(timeout)) is None:
        return None
    try:
        result = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    try:
        payload: Any = json.loads(result.stdout)
    except ValueError:
        return None
    if not isinstance(payload, dict) or payload.get("draft") or payload.get("prerelease"):
        return None
    tag = payload.get("tag_name")
    match = _RELEASE_TAG.fullmatch(tag.strip()) if isinstance(tag, str) else None
    return ".".join(match.groups()) if match else None


def git_safe_env(base: Mapping[str, str] | None = None) -> dict[str, str]:
    """Return an isolated, non-interactive Git environment for public HTTPS."""
    env = dict(os.environ if base is None else base)
    for name in _UNSAFE_GIT_ENV:
        env.pop(name, None)
    for name in tuple(env):
        if name.startswith("GIT_CONFIG_KEY_") or name.startswith("GIT_CONFIG_VALUE_"):
            env.pop(name, None)
    env.update(
        {
            "GIT_TERMINAL_PROMPT": "0",
            "GCM_INTERACTIVE": "never",
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_SYSTEM": os.devnull,
            "GIT_CONFIG_COUNT": str(len(_GIT_CONFIG)),
        }
    )
    for index, (key, value) in enumerate(_GIT_CONFIG):
        env[f"GIT_CONFIG_KEY_{index}"] = key
        env[f"GIT_CONFIG_VALUE_{index}"] = value
    return env


def latest_release_git(timeout: float) -> str | None:
    if timeout <= 0:
        return None
    try:
        with tempfile.TemporaryDirectory(prefix="gafour-update-") as cwd:
            result = subprocess.run(
                ["git", "ls-remote", "--tags", "--refs", REPO_GIT_HTTPS, "v*"],
                capture_output=True,
                text=True,
                timeout=timeout,
                env=git_safe_env(),
                cwd=cwd,
                check=False,
            )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    versions = []
    for line in result.stdout.splitlines():
        if match := _TAG_REF.search(line):
            versions.append(tuple(map(int, match.groups())))
    return ".".join(map(str, max(versions))) if versions else None


def latest_release(timeout: float = 5.0) -> str | None:
    """Return the latest stable release within one aggregate deadline."""
    deadline = time.monotonic() + max(timeout, 0.0)
    reserve = min(2.0, max(timeout / 2, 0.0))
    api_budget = max(deadline - time.monotonic() - reserve, 0.0)
    if api_budget > 0 and (latest := latest_release_api(api_budget)) is not None:
        return latest
    remaining = deadline - time.monotonic()
    return latest_release_git(remaining) if remaining > 0 else None


def installed_version() -> str | None:
    try:
        return metadata.version("gafour")
    except metadata.PackageNotFoundError:
        return None


def _file_url_to_path(value: str) -> str:
    return unquote(urlparse(value).path)


def install_info() -> dict[str, str]:
    direct_url: dict[str, Any] = {}
    for distribution in metadata.distributions(name="gafour"):
        raw = distribution.read_text("direct_url.json")
        if raw:
            try:
                parsed: Any = json.loads(raw)
            except ValueError:
                parsed = None
            if isinstance(parsed, dict):
                direct_url = parsed
        break
    directory = direct_url.get("dir_info")
    if isinstance(directory, dict) and directory.get("editable"):
        raw_url = direct_url.get("url")
        path = _file_url_to_path(raw_url) if isinstance(raw_url, str) else ""
        return {"kind": "editable", "path": path}
    if (Path(sys.prefix) / "uv-receipt.toml").exists():
        return {"kind": "uv", "path": ""}
    return {"kind": "pip", "path": ""}


def install_url(version: str) -> str:
    return f"{REPO_INSTALL_HTTPS}@v{version}"


def upgrade_command(version: str) -> str:
    info = install_info()
    if info["kind"] == "editable":
        path = info.get("path") or "<your gafour checkout>"
        return f"git -C {shlex.quote(path)} pull  # editable install: update your checkout"
    if info["kind"] == "uv":
        argv = ["uv", "tool", "install", "--force", install_url(version)]
    else:
        argv = [sys.executable, "-E", "-m", "pip", "install", "--upgrade", install_url(version)]
    return shlex.join(argv)


def upgrade_argv(version: str) -> list[str] | None:
    info = install_info()
    if info["kind"] == "editable":
        return None
    if info["kind"] == "uv":
        return ["uv", "tool", "install", "--force", install_url(version)]
    return [sys.executable, "-E", "-m", "pip", "install", "--upgrade", install_url(version)]


def perform_upgrade(
    version: str,
    timeout: float = 600.0,
    runner: Callable[..., subprocess.CompletedProcess[str]] | None = None,
) -> subprocess.CompletedProcess[str]:
    argv = upgrade_argv(version)
    if argv is None:
        raise UpgradeError("gafour is an editable install; update its checkout with git pull.")
    run = runner or subprocess.run
    try:
        with tempfile.TemporaryDirectory(prefix="gafour-upgrade-") as cwd:
            result = run(
                argv,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=git_safe_env(),
                cwd=cwd,
                check=False,
            )
    except (OSError, subprocess.SubprocessError) as exc:
        raise UpgradeError(f"Could not run {shlex.join(argv)}: {exc}") from exc
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        message = f"Upgrade failed (exit {result.returncode})."
        raise UpgradeError(f"{message}\n{detail}" if detail else message)
    return result


def _read_cache() -> dict[str, Any]:
    try:
        payload: Any = json.loads(cache_path().read_text())
    except (OSError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _write_cache(latest: str | None) -> None:
    try:
        _write_private(
            cache_path(),
            json.dumps({"checked_at": int(time.time()), "latest": latest}) + "\n",
        )
    except OSError:
        pass


def cached_latest_release() -> str | None:
    cache = _read_cache()
    checked_at = cache.get("checked_at")
    if isinstance(checked_at, (int, float)) and time.time() - checked_at < CHECK_INTERVAL:
        latest = cache.get("latest")
        return latest if isinstance(latest, str) else None
    latest = latest_release()
    _write_cache(latest)
    return latest


def should_check() -> bool:
    if os.environ.get(DISABLE_ENV) or os.environ.get("CI"):
        return False
    try:
        return sys.stderr.isatty()
    except (AttributeError, ValueError):
        return False


def upgrade_notice(latest: str, current: str) -> str:
    return (
        f"A newer gafour release is available: {current} → {latest}\n"
        "Run `gafour upgrade` to install it.\n"
        f"Release notes: {RELEASE_URL}/v{latest}"
    )


def pending_notice() -> str | None:
    """Return a once-daily interactive notice. Never raise."""
    try:
        if not should_check():
            return None
        current = installed_version()
        latest = cached_latest_release()
        if current and latest and is_newer(latest, current):
            return upgrade_notice(latest, current)
    except Exception:
        return None
    return None
