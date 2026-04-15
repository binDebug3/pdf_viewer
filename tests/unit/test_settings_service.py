from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSettings

from services.settings_service import SettingsService


def _build_settings(tmp_path: Path) -> QSettings:
    return QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat)


def test_settings_service_tracks_recent_files_in_mru_order(tmp_path: Path) -> None:
    first = tmp_path / "first.pdf"
    second = tmp_path / "second.pdf"
    first.write_bytes(b"first")
    second.write_bytes(b"second")

    service = SettingsService(settings=_build_settings(tmp_path))
    service.add_recent_file(first)
    service.add_recent_file(second)
    service.add_recent_file(first)

    assert service.recent_files() == [str(first.resolve()), str(second.resolve())]


def test_settings_service_cleans_missing_recent_files(tmp_path: Path) -> None:
    missing = str((tmp_path / "missing.pdf").resolve())
    settings = _build_settings(tmp_path)
    settings.setValue(SettingsService.KEY_RECENT_FILES, [missing])

    service = SettingsService(settings=settings)

    assert service.recent_files() == []


def test_settings_service_handles_last_session_path_and_restore_flag(tmp_path: Path) -> None:
    settings = _build_settings(tmp_path)
    service = SettingsService(settings=settings)

    document = tmp_path / "last.pdf"
    document.write_bytes(b"last")

    service.set_last_session_path(document)
    service.set_restore_last_session(False)

    assert service.last_session_path() == str(document.resolve())
    assert service.should_restore_last_session() is False
