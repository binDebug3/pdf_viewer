from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSettings


class SettingsService:
    """
    Persist lightweight UI preferences and session hints.

    Uses QSettings under the configured organization/application names so values
    are stored in a platform-appropriate location on Windows.
    """

    MAX_RECENT_FILES = 8
    KEY_RECENT_FILES = "recent_files"
    KEY_LAST_SESSION_PATH = "last_session_path"
    KEY_RESTORE_LAST_SESSION = "restore_last_session"

    def __init__(self, settings: QSettings | None = None) -> None:
        self._settings = settings or QSettings()

    def recent_files(self) -> list[str]:
        """
        Return recent PDF paths that still exist on disk.

        Returns:
            List of absolute paths ordered most-recent first.
        """
        raw_value = self._settings.value(self.KEY_RECENT_FILES, [])
        values = self._to_string_list(raw_value)
        existing = [path for path in values if Path(path).exists()]
        if existing != values:
            self._settings.setValue(self.KEY_RECENT_FILES, existing)
        return existing

    def add_recent_file(self, file_path: str | Path) -> None:
        """
        Add a file to the recent list and keep it deduplicated and bounded.

        Args:
            file_path: PDF file path to store.
        """
        normalized_path = str(Path(file_path).resolve())
        items = [path for path in self.recent_files() if path != normalized_path]
        items.insert(0, normalized_path)
        self._settings.setValue(self.KEY_RECENT_FILES, items[: self.MAX_RECENT_FILES])

    def remove_recent_file(self, file_path: str | Path) -> None:
        """
        Remove a path from the recent list if it is present.

        Args:
            file_path: PDF file path to remove.
        """
        normalized_path = str(Path(file_path).resolve())
        remaining = [path for path in self.recent_files() if path != normalized_path]
        self._settings.setValue(self.KEY_RECENT_FILES, remaining)

    def last_session_path(self) -> str | None:
        """
        Return the last loaded session path if available and valid.

        Returns:
            Absolute path string or None when not configured.
        """
        value = self._settings.value(self.KEY_LAST_SESSION_PATH, "")
        if value is None:
            return None
        path = str(value).strip()
        if not path:
            return None
        if not Path(path).exists():
            self.clear_last_session_path()
            return None
        return path

    def set_last_session_path(self, file_path: str | Path) -> None:
        """
        Save the latest opened document path for optional restore.

        Args:
            file_path: PDF file path to persist.
        """
        normalized_path = str(Path(file_path).resolve())
        self._settings.setValue(self.KEY_LAST_SESSION_PATH, normalized_path)

    def clear_last_session_path(self) -> None:
        """
        Clear the stored last-session path.
        """
        self._settings.remove(self.KEY_LAST_SESSION_PATH)

    def should_restore_last_session(self) -> bool:
        """
        Return whether startup should attempt restoring the last session.

        Returns:
            True when restore is enabled, otherwise False.
        """
        raw_value = self._settings.value(self.KEY_RESTORE_LAST_SESSION, True)
        if isinstance(raw_value, bool):
            return raw_value
        return str(raw_value).strip().lower() in {"1", "true", "yes", "on"}

    def set_restore_last_session(self, enabled: bool) -> None:
        """
        Persist the restore-on-startup preference.

        Args:
            enabled: Whether restore should be attempted automatically.
        """
        self._settings.setValue(self.KEY_RESTORE_LAST_SESSION, enabled)

    @staticmethod
    def _to_string_list(value: object) -> list[str]:
        if value is None:
            return []
        if isinstance(value, list):
            return [str(item) for item in value if str(item).strip()]
        if isinstance(value, str):
            return [value] if value.strip() else []
        return [str(value)] if str(value).strip() else []
