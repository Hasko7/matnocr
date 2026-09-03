from matnocr.doctor import run_doctor_checks


def test_doctor_reports_every_required_check() -> None:
    checks = run_doctor_checks()
    labels = {check.label for check in checks}

    assert labels == {
        "Supported Windows",
        "Windows.Media.Ocr",
        "Installed OCR languages",
        "PDF renderer",
        "Direct-RAM conversion",
        "Maximum image dimension",
        "Python",
        "MatnOCR",
    }
    assert all(check.details for check in checks)
