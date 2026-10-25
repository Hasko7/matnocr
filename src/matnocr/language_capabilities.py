"""Administrative Windows OCR language capability management."""

import base64
import ctypes
import json
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent
from typing import Literal

from winrt.windows.globalization import Language

CapabilityAction = Literal["install", "remove"]
LANGUAGE_TAG_PATTERN = re.compile(r"^[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8})+$")
WINDOWS_POWERSHELL = "powershell.exe"


class LanguageCapabilityError(RuntimeError):
    """Raised when an OCR language capability cannot be managed safely."""


@dataclass(frozen=True, slots=True)
class LanguageCapabilityResult:
    """Result of one completed Windows capability operation."""

    language_tag: str
    action: CapabilityAction
    elevated_window_opened: bool


@dataclass(frozen=True, slots=True)
class OcrCapability:
    """One Windows OCR language capability and its current state."""

    language_tag: str
    state: str
    display_name: str = ""


@dataclass(frozen=True, slots=True)
class CapabilityCatalogResult:
    """Dynamically queried Windows OCR language capability catalog."""

    capabilities: tuple[OcrCapability, ...]
    elevated_window_opened: bool


def normalize_capability_language_tag(language_tag: str) -> str:
    """Validate and normalize a complete OCR capability language tag."""

    value = language_tag.strip()
    if not LANGUAGE_TAG_PATTERN.fullmatch(value):
        raise LanguageCapabilityError(
            "A complete language code is required, for example fr-FR or "
            "sr-LATN-RS. Run 'matnocr languages available' to see the valid "
            "codes, then use 'matnocr languages install <code>'."
        )

    language, *subtags = value.split("-")
    return "-".join([language.lower(), *(subtag.upper() for subtag in subtags)])


def make_ocr_capability_name(language_tag: str) -> str:
    """Return the Windows capability name for a validated language tag."""

    normalized = normalize_capability_language_tag(language_tag)
    return f"Language.OCR~~~{normalized}~0.0.1.0"


def is_running_as_administrator() -> bool:
    """Return whether the current Windows process has administrator rights."""

    if sys.platform != "win32":
        return False

    windll = getattr(ctypes, "windll", None)
    if windll is None:
        return False

    try:
        return bool(windll.shell32.IsUserAnAdmin())
    except OSError:
        return False


def _powershell_script(
    action: CapabilityAction,
    language_tag: str,
    *,
    pause: bool,
) -> str:
    capability_name = make_ocr_capability_name(language_tag)
    cmdlet = (
        "Add-WindowsCapability" if action == "install" else "Remove-WindowsCapability"
    )
    desired_state = "Installed" if action == "install" else "NotPresent"
    action_label = "installed" if action == "install" else "removed"
    pause_script = (
        "Write-Host ''; Read-Host 'Press Enter to close this window' | Out-Null"
        if pause
        else ""
    )

    return dedent(
        f"""
        $ErrorActionPreference = 'Stop'
        $exitCode = 0
        $capabilityName = '{capability_name}'
        try {{
            $capability = Get-WindowsCapability -Online -Name $capabilityName
            if ($null -eq $capability) {{
                throw "Windows does not provide OCR capability {capability_name}."
            }}
            if ($capability.State -ne '{desired_state}') {{
                {cmdlet} -Online -Name $capabilityName | Out-Null
            }}
            $final = Get-WindowsCapability -Online -Name $capabilityName
            if ($null -eq $final -or $final.State -ne '{desired_state}') {{
                throw "OCR capability did not reach state {desired_state}."
            }}
            Write-Host 'OCR language {language_tag} {action_label} successfully.' -ForegroundColor Green
        }} catch {{
            Write-Host ('OCR language operation failed: ' + $_.Exception.Message) -ForegroundColor Red
            $exitCode = 1
        }}
        {pause_script}
        exit $exitCode
        """
    ).strip()


def _encode_powershell_script(script: str) -> str:
    return base64.b64encode(script.encode("utf-16-le")).decode("ascii")


def _run_process(arguments: list[str]) -> int:
    try:
        completed = subprocess.run(arguments, check=False)
    except OSError as error:
        raise LanguageCapabilityError(
            "Windows PowerShell could not be started."
        ) from error
    return completed.returncode


def _run_powershell_script(script: str, *, elevate: bool) -> int:
    encoded_script = _encode_powershell_script(script)

    if not elevate:
        arguments = [
            WINDOWS_POWERSHELL,
            "-NoProfile",
            "-NonInteractive",
            "-EncodedCommand",
            encoded_script,
        ]
    else:
        launcher = (
            "$ErrorActionPreference = 'Stop'; "
            "$process = Start-Process -FilePath 'powershell.exe' "
            "-ArgumentList @('-NoProfile','-EncodedCommand',"
            f"'{encoded_script}') -Verb RunAs -PassThru -Wait; "
            "exit $process.ExitCode"
        )
        arguments = [
            WINDOWS_POWERSHELL,
            "-NoProfile",
            "-NonInteractive",
            "-Command",
            launcher,
        ]

    return _run_process(arguments)


def _capability_query_script(output_path: Path) -> str:
    escaped_path = str(output_path).replace("'", "''")
    return dedent(
        f"""
        $ErrorActionPreference = 'Stop'
        $items = @(Get-WindowsCapability -Online -Name 'Language.OCR*' |
            ForEach-Object {{
                [PSCustomObject]@{{
                    Name = $_.Name
                    State = [string]$_.State
                }}
            }})
        ConvertTo-Json -InputObject $items -Compress |
            Set-Content -LiteralPath '{escaped_path}' -Encoding UTF8
        """
    ).strip()


def _run_capability_query(output_path: Path, *, elevate: bool) -> int:
    return _run_powershell_script(
        _capability_query_script(output_path),
        elevate=elevate,
    )


def _parse_capability_catalog(payload: str) -> tuple[OcrCapability, ...]:
    try:
        decoded = json.loads(payload)
    except json.JSONDecodeError as error:
        raise LanguageCapabilityError(
            "Windows returned an invalid OCR capability list."
        ) from error

    if not isinstance(decoded, list):
        raise LanguageCapabilityError(
            "Windows returned an unexpected OCR capability list."
        )

    capabilities: list[OcrCapability] = []
    pattern = re.compile(r"^Language\.OCR~~~(.+)~0\.0\.1\.0$", re.IGNORECASE)
    for item in decoded:
        if not isinstance(item, dict):
            continue
        name = item.get("Name")
        state = item.get("State")
        if not isinstance(name, str) or not isinstance(state, str):
            continue
        match = pattern.fullmatch(name)
        if match is None:
            continue
        language_tag = match.group(1)
        try:
            display_name = Language(language_tag).display_name
        except (OSError, RuntimeError, ValueError):
            display_name = language_tag
        capabilities.append(OcrCapability(language_tag, state, display_name))

    return tuple(sorted(capabilities, key=lambda item: item.language_tag.lower()))


def get_language_capabilities() -> CapabilityCatalogResult:
    """Query all Windows OCR capabilities, elevating through UAC when needed."""

    if sys.platform != "win32":
        raise LanguageCapabilityError(
            "Windows OCR language capabilities can only be queried on Windows."
        )

    elevate = not is_running_as_administrator()
    descriptor, temporary_name = tempfile.mkstemp(
        prefix="matnocr-ocr-languages-",
        suffix=".json",
    )
    os.close(descriptor)
    output_path = Path(temporary_name)

    try:
        return_code = _run_capability_query(output_path, elevate=elevate)
        if return_code != 0:
            raise LanguageCapabilityError(
                "The OCR language catalog could not be read. "
                "Administrator approval may have been cancelled."
            )
        payload = output_path.read_text(encoding="utf-8-sig")
        capabilities = _parse_capability_catalog(payload)
    except OSError as error:
        raise LanguageCapabilityError(
            "The OCR language catalog could not be read."
        ) from error
    finally:
        output_path.unlink(missing_ok=True)

    return CapabilityCatalogResult(capabilities, elevate)


def manage_language_capability(
    action: CapabilityAction,
    language_tag: str,
) -> LanguageCapabilityResult:
    """Install or remove an OCR capability, elevating through UAC when needed."""

    if sys.platform != "win32":
        raise LanguageCapabilityError(
            "Windows OCR language capabilities can only be managed on Windows."
        )
    if action not in {"install", "remove"}:
        raise LanguageCapabilityError(f"Unsupported capability action: {action}")

    normalized = normalize_capability_language_tag(language_tag)
    already_admin = is_running_as_administrator()
    script = _powershell_script(action, normalized, pause=not already_admin)
    return_code = _run_powershell_script(script, elevate=not already_admin)
    if return_code != 0:
        raise LanguageCapabilityError(
            "The OCR language operation did not complete. "
            "Administrator approval may have been cancelled; see the "
            "Windows PowerShell window for details."
        )

    return LanguageCapabilityResult(
        language_tag=normalized,
        action=action,
        elevated_window_opened=not already_admin,
    )
