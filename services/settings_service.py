from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSettings


class SettingsService:
    OVERWRITE_EXPORT_KEY = "export/overwrite_existing"
    LAST_EXPORT_DIR_KEY = "export/last_directory"

    def __init__(self) -> None:
        self._settings = QSettings("pdf_viewer", "pdf_viewer")

    @property
    def overwrite_existing(self) -> bool:
        value = self._settings.value(self.OVERWRITE_EXPORT_KEY, False)
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() in {"1", "true", "yes", "on"}

    def set_overwrite_existing(self, enabled: bool) -> None:
        self._settings.setValue(self.OVERWRITE_EXPORT_KEY, enabled)

    @property
    def last_export_directory(self) -> Path | None:
        value = self._settings.value(self.LAST_EXPORT_DIR_KEY, "")
        if not value:
            return None
        path = Path(str(value))
        return path if path.exists() else None

    def set_last_export_directory(self, directory: Path) -> None:
        self._settings.setValue(self.LAST_EXPORT_DIR_KEY, str(directory))
