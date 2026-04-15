from __future__ import annotations

import logging
from pathlib import Path

from services import runtime_logging
from services.runtime_logging import (
    configure_runtime_logging,
    install_global_exception_hooks,
    write_crash_report,
)


def _reset_runtime_logging_state() -> None:
    root = logging.getLogger()
    root._pdf_viewer_logging_configured = False
    root._pdf_viewer_exception_hook_installed = False
    root._pdf_viewer_log_path = None


def test_configure_runtime_logging_creates_log_file(tmp_path: Path) -> None:
    _reset_runtime_logging_state()

    log_path = configure_runtime_logging(log_root=tmp_path)

    assert log_path.exists()
    assert log_path.name == "app.log"
    assert log_path.parent.name == "logs"


def test_configure_runtime_logging_reuses_existing_configuration(tmp_path: Path) -> None:
    _reset_runtime_logging_state()

    first_path = configure_runtime_logging(log_root=tmp_path)
    second_path = configure_runtime_logging(log_root=tmp_path / "other")

    assert second_path == first_path


def test_write_crash_report_creates_report_file(tmp_path: Path) -> None:
    _reset_runtime_logging_state()

    try:
        raise RuntimeError("phase9 crash report smoke")
    except RuntimeError as error:
        crash_path = write_crash_report(
            type(error),
            error,
            error.__traceback__,
            crash_root=tmp_path,
        )

    report_text = crash_path.read_text(encoding="utf-8")
    assert crash_path.exists()
    assert crash_path.parent.name == "crashes"
    assert "RuntimeError" in report_text
    assert "phase9 crash report smoke" in report_text


def test_install_global_exception_hooks_handles_uncaught_exception(tmp_path: Path) -> None:
    _reset_runtime_logging_state()
    captured: dict[str, Path] = {}

    original_write_crash_report = runtime_logging.write_crash_report
    original_show_crash_dialog = runtime_logging._show_crash_dialog
    try:

        def fake_write_crash_report(exc_type, exc_value, exc_traceback, crash_root=None) -> Path:
            path = tmp_path / "crashes" / "simulated.log"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("simulated", encoding="utf-8")
            captured["path"] = path
            return path

        def fake_show_crash_dialog(crash_path: Path) -> None:
            captured["dialog"] = crash_path

        runtime_logging.write_crash_report = fake_write_crash_report
        runtime_logging._show_crash_dialog = fake_show_crash_dialog

        install_global_exception_hooks(log_root=tmp_path)
        try:
            raise ValueError("boom")
        except ValueError as error:
            assert error.__traceback__ is not None
            runtime_logging.sys.excepthook(type(error), error, error.__traceback__)
    finally:
        runtime_logging.write_crash_report = original_write_crash_report
        runtime_logging._show_crash_dialog = original_show_crash_dialog

    assert captured["path"].exists()
    assert captured["dialog"] == captured["path"]


def test_install_global_exception_hooks_is_idempotent(tmp_path: Path) -> None:
    _reset_runtime_logging_state()

    install_global_exception_hooks(log_root=tmp_path)
    first_hook = runtime_logging.sys.excepthook
    install_global_exception_hooks(log_root=tmp_path)

    assert runtime_logging.sys.excepthook is first_hook
