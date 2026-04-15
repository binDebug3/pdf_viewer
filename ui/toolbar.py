from __future__ import annotations

from collections.abc import Callable

from PySide6.QtGui import QAction
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
            ("open", "Open PDF"),
            ("add", "Add PDF"),
            ("save_as", "Save As"),
            ("split", "Split"),
            ("save_splits", "Save Splits"),
            ("cancel_split", "Cancel Split"),
            ("join", "Join"),
            ("rotate", "Rotate"),
            ("duplicate", "Duplicate"),
            ("delete", "Delete"),
            ("undo", "Undo"),
            ("redo", "Redo"),
        ]

        for index, (action_id, label) in enumerate(action_specs):
            action = QAction(label, self)
            action.triggered.connect(lambda _checked=False, value=action_id: on_action(value))
            self._actions[action_id] = action
            self.addAction(action)
            if action_id in {"save_splits", "cancel_split"}:
                action.setVisible(False)
            if index in {2, 6, 9}:
                self.addSeparator()

    def set_split_mode(self, active: bool) -> None:
        self._actions["split"].setText("Split Active" if active else "Split")
        self._actions["split"].setEnabled(not active)
        self._actions["save_splits"].setVisible(active)
        self._actions["save_splits"].setEnabled(active)
        self._actions["cancel_split"].setVisible(active)
        self._actions["cancel_split"].setEnabled(active)

    def set_history_state(self, can_undo: bool, can_redo: bool) -> None:
        self._actions["undo"].setEnabled(can_undo)
        self._actions["redo"].setEnabled(can_redo)
