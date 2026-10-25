import base64
from pathlib import Path
from types import SimpleNamespace

import pytest

from matnocr import language_capabilities


@pytest.mark.parametrize(
    ("requested", "expected"),
    [
        ("fr-fr", "fr-FR"),
        (" ar-SA ", "ar-SA"),
        ("sr-latn-rs", "sr-LATN-RS"),
    ],
)
def test_normalize_capability_language_tag(
    requested: str,
    expected: str,
) -> None:
    assert (
        language_capabilities.normalize_capability_language_tag(requested) == expected
    )


@pytest.mark.parametrize("requested", ["fr", "fr FR", "fr-FR'; exit", ""])
def test_invalid_capability_language_tag_is_rejected(requested: str) -> None:
    with pytest.raises(language_capabilities.LanguageCapabilityError):
        language_capabilities.normalize_capability_language_tag(requested)


def test_capability_name_uses_windows_ocr_format() -> None:
    assert language_capabilities.make_ocr_capability_name("fr-FR") == (
        "Language.OCR~~~fr-FR~0.0.1.0"
    )


def test_capability_catalog_is_parsed_and_sorted() -> None:
    payload = """[
        {"Name":"Language.OCR~~~fr-FR~0.0.1.0","State":"NotPresent"},
        {"Name":"Language.OCR~~~ar-SA~0.0.1.0","State":"Installed"}
    ]"""

    capabilities = language_capabilities._parse_capability_catalog(payload)

    assert [item.language_tag for item in capabilities] == ["ar-SA", "fr-FR"]
    assert [item.state for item in capabilities] == ["Installed", "NotPresent"]
    assert all(item.display_name for item in capabilities)


def test_available_capabilities_use_elevated_dynamic_query(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(language_capabilities.sys, "platform", "win32")
    monkeypatch.setattr(
        language_capabilities,
        "is_running_as_administrator",
        lambda: False,
    )

    def fake_query(output_path: Path, *, elevate: bool) -> int:
        assert elevate
        output_path.write_text(
            '[{"Name":"Language.OCR~~~fr-FR~0.0.1.0","State":"NotPresent"}]',
            encoding="utf-8",
        )
        return 0

    monkeypatch.setattr(
        language_capabilities,
        "_run_capability_query",
        fake_query,
    )

    result = language_capabilities.get_language_capabilities()

    assert result.elevated_window_opened
    assert len(result.capabilities) == 1
    assert result.capabilities[0].language_tag == "fr-FR"
    assert result.capabilities[0].state == "NotPresent"
    assert result.capabilities[0].display_name


def test_non_admin_operation_launches_elevated_windows_powershell(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: list[str] = []
    monkeypatch.setattr(language_capabilities.sys, "platform", "win32")
    monkeypatch.setattr(
        language_capabilities,
        "is_running_as_administrator",
        lambda: False,
    )

    def fake_run(arguments: list[str], *, check: bool) -> object:
        assert not check
        captured.extend(arguments)
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(language_capabilities.subprocess, "run", fake_run)

    result = language_capabilities.manage_language_capability("install", "fr-FR")

    assert result.elevated_window_opened
    assert "-Command" in captured
    launcher = captured[-1]
    assert "Start-Process" in launcher
    assert "-Verb RunAs" in launcher

    encoded_script = launcher.split("'-NoProfile','-EncodedCommand','", maxsplit=1)[1]
    encoded_script = encoded_script.split("'", maxsplit=1)[0]
    script = base64.b64decode(encoded_script).decode("utf-16-le")
    assert "Add-WindowsCapability" in script
    assert "Language.OCR~~~fr-FR~0.0.1.0" in script
    assert "Get-WindowsCapability" in script


def test_admin_remove_runs_directly_and_checks_final_state(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: list[str] = []
    monkeypatch.setattr(language_capabilities.sys, "platform", "win32")
    monkeypatch.setattr(
        language_capabilities,
        "is_running_as_administrator",
        lambda: True,
    )

    def fake_run(arguments: list[str], *, check: bool) -> object:
        assert not check
        captured.extend(arguments)
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(language_capabilities.subprocess, "run", fake_run)

    result = language_capabilities.manage_language_capability("remove", "fr-FR")

    assert not result.elevated_window_opened
    assert "-EncodedCommand" in captured
    encoded_script = captured[-1]
    script = base64.b64decode(encoded_script).decode("utf-16-le")
    assert "Remove-WindowsCapability" in script
    assert "$final = Get-WindowsCapability" in script
    assert "NotPresent" in script


def test_failed_operation_is_reported(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(language_capabilities.sys, "platform", "win32")
    monkeypatch.setattr(
        language_capabilities,
        "is_running_as_administrator",
        lambda: True,
    )
    monkeypatch.setattr(
        language_capabilities.subprocess,
        "run",
        lambda *_args, **_kwargs: SimpleNamespace(returncode=1),
    )

    with pytest.raises(
        language_capabilities.LanguageCapabilityError,
        match="did not complete",
    ):
        language_capabilities.manage_language_capability("install", "fr-FR")
