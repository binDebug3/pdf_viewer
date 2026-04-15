from __future__ import annotations

from collections.abc import Callable

from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QToolBar


class AppToolBar(QToolBar):
    def __init__(self, on_action: Callable[[str], None], parent=None) -> None:
        super().__init__("Primary actions", parent)
        self.setObjectName("PrimaryToolbar")
        self.setMovable(False)
        self.setFloatable(False)
        self.setIconSize(self.iconSize())
        self.setToolButtonStyle(self.toolButtonStyle())
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.PreventContextMenu)
        self._actions: dict[str, QAction] = {}
        self._build_actions(on_action)

    def _build_actions(self, on_action: Callable[[str], None]) -> None:
        action_specs = [
            ("open", "Open PDF", QKeySequence.StandardKey.Open),
            ("add", "Add PDF", "Ctrl+Shift+O"),
            ("save_as", "Save As", QKeySequence.StandardKey.SaveAs),
            ("split", "Split", "Ctrl+Shift+L"),
            ("save_splits", "Save Splits", "Ctrl+Shift+E"),
            ("cancel_split", "Cancel Split", "Esc"),
            ("join", "Join", "Ctrl+J"),
            ("rotate", "Rotate", "Ctrl+R"),
            ("duplicate", "Duplicate", QKeySequence.StandardKey.Copy),
            ("delete", "Delete", QKeySequence.StandardKey.Delete),
            ("undo", "Undo", QKeySequence.StandardKey.Undo),
            ("redo", "Redo", QKeySequence.StandardKey.Redo),
        ]

        for index, (action_id, label, shortcut) in enumerate(action_specs):
            action = QAction(label, self)
            action.setShortcut(shortcut)
            action.setShortcutContext(Qt.ShortcutContext.WindowShortcut)
            action.setStatusTip(label)
            action.setToolTip(f"{label} ({action.shortcut().toString()})")
            if action_id == "split":
                action.setCheckable(True)
            action.triggered.connect(lambda _checked=False, value=action_id: on_action(value))
            self._actions[action_id] = action
            self.addAction(action)
            if action_id in {"save_splits", "cancel_split"}:
                action.setVisible(False)
            if index in {2, 6, 9}:
                self.addSeparator()

    def set_split_mode(self, active: bool) -> None:
        self._actions["split"].setText("Split Active" if active else "Split")
        self._actions["split"].setChecked(active)
        self._actions["split"].setEnabled(True)
        self._actions["save_splits"].setVisible(active)
        self._actions["save_splits"].setEnabled(active)
        self._actions["cancel_split"].setVisible(active)
        self._actions["cancel_split"].setEnabled(active)

    def set_history_state(self, can_undo: bool, can_redo: bool) -> None:
        self._actions["undo"].setEnabled(can_undo)
        self._actions["redo"].setEnabled(can_redo)
