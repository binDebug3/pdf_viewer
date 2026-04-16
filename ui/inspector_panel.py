from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)


class InspectorPanel(QFrame):
    split_options_changed = Signal(str, str, bool)
    split_reset_requested = Signal()
    split_apply_requested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("SidebarPlaceholder")
        self.setFixedWidth(280)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        title = QLabel("Details", self)
        title.setObjectName("SectionTitle")

        self._summary = QLabel("Current state: blank workspace", self)
        self._summary.setObjectName("MutedText")
        self._summary.setWordWrap(True)

        self._details = QLabel(
            "Open or add a PDF to inspect page count, selection, and split readiness.",
            self,
        )
        self._details.setObjectName("MutedText")
        self._details.setWordWrap(True)

        split_title = QLabel("Split plan", self)
        split_title.setObjectName("SectionTitle")

        self._split_mode = QComboBox(self)
        self._split_mode.addItem("Current page", "current")
        self._split_mode.addItem("Selected pages", "selected")
        self._split_mode.addItem("Custom page ranges", "custom")
        self._split_mode.addItem("Odd pages", "odd")
        self._split_mode.addItem("Even pages", "even")

        self._custom_ranges = QLineEdit(self)
        self._custom_ranges.setPlaceholderText("Examples: 1,3-5,8")

        self._create_multiple = QCheckBox("Create one PDF per chosen page", self)

        action_row = QHBoxLayout()
        self._reset_split = QPushButton("Cancel Split", self)
        self._apply_split = QPushButton("Save Splits", self)
        action_row.addWidget(self._reset_split)
        action_row.addWidget(self._apply_split)

        self._split_preview = QLabel("Preview will appear when split mode is active.", self)
        self._split_preview.setObjectName("MutedText")
        self._split_preview.setWordWrap(True)

        self._split_mode.currentIndexChanged.connect(self._emit_split_options)
        self._custom_ranges.textChanged.connect(self._emit_split_options)
        self._create_multiple.stateChanged.connect(self._emit_split_options)
        self._apply_split.clicked.connect(self._emit_split_apply)
        self._reset_split.clicked.connect(self._emit_split_reset)

        layout.addWidget(title)
        layout.addWidget(self._summary)
        layout.addWidget(self._details)
        layout.addWidget(split_title)
        layout.addWidget(self._split_mode)
        layout.addWidget(self._custom_ranges)
        layout.addWidget(self._create_multiple)
        layout.addLayout(action_row)
        layout.addWidget(self._split_preview)
        layout.addStretch(1)

        self._set_split_controls_enabled(False)

    def set_blank_state(self) -> None:
        self._summary.setText("Current state: blank workspace")
        self._details.setText(
            "Open a PDF from the toolbar or File menu, then select pages to edit or split."
        )
        self._split_preview.setText(
            "Enter split mode to preview output groups before saving split files."
        )
        self._set_split_controls_enabled(False)

    def set_split_controls(
        self,
        mode: str,
        custom_ranges: str,
        create_multiple_files: bool,
    ) -> None:
        mode_index = self._split_mode.findData(mode)
        if mode_index >= 0 and self._split_mode.currentIndex() != mode_index:
            self._split_mode.blockSignals(True)
            self._split_mode.setCurrentIndex(mode_index)
            self._split_mode.blockSignals(False)

        self._custom_ranges.blockSignals(True)
        self._custom_ranges.setText(custom_ranges)
        self._custom_ranges.blockSignals(False)

        self._create_multiple.blockSignals(True)
        self._create_multiple.setChecked(create_multiple_files)
        self._create_multiple.blockSignals(False)

        self._update_custom_visibility()

    def set_split_preview(self, text: str) -> None:
        self._split_preview.setText(text)

    def set_document_state(
        self,
        file_path: str,
        page_count: int,
        selected_page_index: int,
        source_count: int = 1,
        selected_count: int = 1,
        split_mode_active: bool = False,
        split_start_indexes: list[int] | None = None,
        split_preview_lines: list[str] | None = None,
    ) -> None:
        split_start_indexes = split_start_indexes or []
        split_preview_lines = split_preview_lines or []
        self._set_split_controls_enabled(split_mode_active)
        if split_mode_active:
            preview_text = "\n".join(split_preview_lines[:6])
            if len(split_preview_lines) > 6:
                preview_text += "\n..."
            self._summary.setText(f"File: {Path(file_path).name}\nSplit mode active")
            self._details.setText(
                f"Documents: {source_count}\n"
                f"Pages: {page_count}\n"
                f"Selected page: {selected_page_index + 1}\n"
                f"Selected count: {selected_count}\n"
                f"Output files: {max(1, len(split_preview_lines))}\n"
                "Preview:\n"
                f"{preview_text}\n"
                "Adjust split controls, review preview, then click Save Splits."
            )
            return

        self._summary.setText(f"File: {Path(file_path).name}")
        self._details.setText(
            f"Documents: {source_count}\n"
            f"Pages: {page_count}\n"
            f"Selected page: {selected_page_index + 1}\n"
            f"Selected count: {selected_count}\n"
            "Tip: Use Ctrl+O to open, Ctrl+Shift+O to add, and drag pages to reorder."
        )

    def _emit_split_options(self) -> None:
        self._update_custom_visibility()
        self.split_options_changed.emit(
            str(self._split_mode.currentData()),
            self._custom_ranges.text().strip(),
            self._create_multiple.isChecked(),
        )

    def _emit_split_apply(self) -> None:
        self._emit_split_options()
        self.split_apply_requested.emit()

    def _emit_split_reset(self) -> None:
        self.split_reset_requested.emit()

    def _set_split_controls_enabled(self, enabled: bool) -> None:
        self._split_mode.setEnabled(enabled)
        self._custom_ranges.setEnabled(enabled)
        self._create_multiple.setEnabled(enabled)
        self._reset_split.setEnabled(enabled)
        self._apply_split.setEnabled(enabled)
        self._update_custom_visibility()

    def _update_custom_visibility(self) -> None:
        is_custom = self._split_mode.currentData() == "custom"
        self._custom_ranges.setVisible(is_custom)
