from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
)

from core.models.split_spec import SplitSpec


class SplitDialog(QDialog):
    def __init__(self, current_page: int, selected_count: int, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Split PDF")
        self.setModal(True)
        self.resize(420, 220)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        summary = QLabel(
            f"Current page: {current_page + 1}\nSelected pages: {selected_count}",
            self,
        )
        summary.setWordWrap(True)

        form = QFormLayout()
        form.setSpacing(10)

        self._mode = QComboBox(self)
        self._mode.addItem("Current page", "current")
        self._mode.addItem("Selected pages", "selected")
        self._mode.addItem("Odd pages", "odd")
        self._mode.addItem("Even pages", "even")
        self._mode.addItem("Custom page range", "custom")
        self._mode.currentIndexChanged.connect(self._update_custom_visibility)

        self._custom_ranges = QLineEdit(self)
        self._custom_ranges.setPlaceholderText("Examples: 1,3-5,8")

        self._multiple = QCheckBox("Create one PDF per chosen page", self)

        form.addRow("Split source", self._mode)
        form.addRow("Custom pages", self._custom_ranges)
        form.addRow("Output", self._multiple)

        self._buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            self,
        )
        self._buttons.accepted.connect(self._accept)
        self._buttons.rejected.connect(self.reject)

        layout.addWidget(summary)
        layout.addLayout(form)
        layout.addWidget(self._buttons)

        self._update_custom_visibility()

    def split_spec(self) -> SplitSpec:
        return SplitSpec(
            mode=self._mode.currentData(),
            custom_ranges=self._custom_ranges.text().strip(),
            create_multiple_files=self._multiple.isChecked(),
        )

    def _update_custom_visibility(self) -> None:
        is_custom = self._mode.currentData() == "custom"
        self._custom_ranges.setVisible(is_custom)

    def _accept(self) -> None:
        spec = self.split_spec()
        if spec.mode == "custom" and not spec.custom_ranges:
            QMessageBox.warning(self, "Split PDF", "Enter at least one page number or range.")
            return
        self.accept()
