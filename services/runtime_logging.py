from __future__ import annotations

import logging
import logging.handlers
import os
import platform
import sys
import threading
import traceback
from datetime import datetime, timezone
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMessageBox

APP_DIRECTORY_NAME = "pdf_viewer"
LOG_DIRECTORY_NAME = "logs"
CRASH_DIRECTORY_NAME = "crashes"
APP_LOG_FILENAME = "app.log"
MAX_LOG_BYTES = 1_000_000
LOG_BACKUP_COUNT = 5


def configure_runtime_logging(log_root: Path | None = None) -> Path:
    """
    Configure rotating file and console logging for runtime diagnostics.

    Returns:
        Path to the active application log file.
    """
    root = logging.getLogger()
    if getattr(root, "_pdf_viewer_logging_configured", False):
        existing_path = getattr(root, "_pdf_viewer_log_path", None)
        if isinstance(existing_path, Path):
            return existing_path

    resolved_root = _resolve_runtime_root(log_root)
    log_directory = resolved_root / LOG_DIRECTORY_NAME
    log_directory.mkdir(parents=True, exist_ok=True)
    log_path = log_directory / APP_LOG_FILENAME

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.handlers.RotatingFileHandler(
        log_path,
        maxBytes=MAX_LOG_BYTES,
        backupCount=LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)

    root.setLevel(logging.INFO)
    root.handlers.clear()
    root.addHandler(file_handler)
    root.addHandler(stream_handler)

    root._pdf_viewer_logging_configured = True
    root._pdf_viewer_log_path = log_path
    logging.getLogger(__name__).info("Runtime logging configured: %s", log_path)
    return log_path


def install_global_exception_hooks(log_root: Path | None = None) -> None:
    """
    Install process-wide hooks to capture uncaught exceptions.

    Args:
        log_root: Optional root directory used to store generated crash reports.
    """
    root = logging.getLogger()
    if getattr(root, "_pdf_viewer_exception_hook_installed", False):
        logging.getLogger(__name__).info("Global exception hooks already installed.")
        return

    resolved_root = _resolve_runtime_root(log_root)
    logger = logging.getLogger(__name__)

    def _exception_hook(exc_type, exc_value, exc_traceback) -> None:
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        crash_report = write_crash_report(
            exc_type,
            exc_value,
            exc_traceback,
            crash_root=resolved_root,
        )
        logger.critical(
            "Unhandled exception captured. Crash report: %s",
            crash_report,
            exc_info=(exc_type, exc_value, exc_traceback),
        )
        _show_crash_dialog(crash_report)

    def _thread_exception_hook(args: threading.ExceptHookArgs) -> None:
        _exception_hook(args.exc_type, args.exc_value, args.exc_traceback)

    sys.excepthook = _exception_hook
    threading.excepthook = _thread_exception_hook
    root._pdf_viewer_exception_hook_installed = True
    logger.info("Global exception hooks installed.")


def write_crash_report(
    exc_type: type[BaseException],
    exc_value: BaseException,
    exc_traceback,
    crash_root: Path | None = None,
) -> Path:
    """
    Write a detailed crash report for an uncaught exception.

    Args:
        exc_type: Exception class.
        exc_value: Exception instance.
        exc_traceback: Traceback for the uncaught exception.
        crash_root: Optional runtime root for writing crash reports.

    Returns:
        Path to the created crash report.
    """
    resolved_root = _resolve_runtime_root(crash_root)
    crash_directory = resolved_root / CRASH_DIRECTORY_NAME
    crash_directory.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
    crash_report_path = crash_directory / f"crash_{timestamp}.log"
    formatted_exception = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    report_body = (
        f"UTC Time: {datetime.now(tz=timezone.utc).isoformat()}\n"
        f"Python Version: {platform.python_version()}\n"
        f"Platform: {platform.platform()}\n"
        f"Executable: {sys.executable}\n"
        f"Application Version: beta\n"
        f"\n"
        f"Unhandled Exception:\n"
        f"{formatted_exception}"
    )
    crash_report_path.write_text(report_body, encoding="utf-8")
    logging.getLogger(__name__).info("Crash report written: %s", crash_report_path)
    return crash_report_path


def _resolve_runtime_root(log_root: Path | None) -> Path:
    if log_root is not None:
        root = Path(log_root)
    else:
        local_app_data = os.getenv("LOCALAPPDATA")
        if local_app_data:
            root = Path(local_app_data) / APP_DIRECTORY_NAME
        else:
            root = Path.home() / f".{APP_DIRECTORY_NAME}"
    root.mkdir(parents=True, exist_ok=True)
    return root


def _show_crash_dialog(crash_report_path: Path) -> None:
    application = QApplication.instance()
    if application is None:
        return
    QMessageBox.critical(
        None,
        "Unexpected error",
        (
            "The application encountered an unexpected error. "
            f"A crash report was written to:\n{crash_report_path}"
        ),
    )
