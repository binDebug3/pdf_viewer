from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout


class InspectorPanel(QFrame):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("SidebarPlaceholder")
        self.setFixedWidth(220)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        title = QLabel("Details", self)
        title.setObjectName("SectionTitle")

        self._summary = QLabel("Current state: blank workspace", self)
        self._summary.setObjectName("MutedText")
        self._summary.setWordWrap(True)

        self._details = QLabel("Open a PDF to inspect page count and current selection.", self)
        self._details.setObjectName("MutedText")
        self._details.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(self._summary)
        layout.addWidget(self._details)
        layout.addStretch(1)

    def set_blank_state(self) -> None:
        self._summary.setText("Current state: blank workspace")
        self._details.setText("Open a PDF to inspect page count and current selection.")

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
        if split_mode_active:
            split_start_pages = [1] + [index + 1 for index in split_start_indexes]
            split_start_text = ", ".join(str(page_number) for page_number in split_start_pages)
            preview_text = "\n".join(split_preview_lines[:6])
            if len(split_preview_lines) > 6:
                preview_text += "\n..."
            self._summary.setText(f"File: {Path(file_path).name}\nSplit mode active")
            self._details.setText(
                f"Documents: {source_count}\n"
                f"Pages: {page_count}\n"
                f"Selected page: {selected_page_index + 1}\n"
                f"Selected count: {selected_count}\n"
                f"Split starts: {split_start_text}\n"
                f"Output files: {len(split_start_pages)}\n"
                "Preview:\n"
                f"{preview_text}\n"
                "Click filmstrip pages to toggle split starts, then click Save Splits."
            )
            return

        self._summary.setText(f"File: {Path(file_path).name}")
        self._details.setText(
            f"Documents: {source_count}\n"
            f"Pages: {page_count}\n"
            f"Selected page: {selected_page_index + 1}\n"
            f"Selected count: {selected_count}\n"
            "Split, export, and page actions will appear here."
        )
