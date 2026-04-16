from __future__ import annotations

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFrame, QLabel, QScrollArea, QVBoxLayout


class ViewerPanel(QFrame):
    higher_resolution_render_requested = Signal(int)
    MIN_RENDER_TARGET_WIDTH = 1800
    RENDER_TARGET_MULTIPLIER = 3.0
    RERENDER_TRIGGER_RATIO = 1.1

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("ViewerPanelContainer")
        self._source_pixmap = QPixmap()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._page_label = QLabel(self)
        self._page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._page_label.setObjectName("PageCanvas")
        self._page_label.setMinimumHeight(280)
        self._page_label.setText(
            "Open a PDF to start. Then add PDFs, reorder pages, and build split plans here."
        )

        self._scroll_area = QScrollArea(self)
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll_area.viewport().installEventFilter(self)

        scroll_content = QFrame(self._scroll_area)
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.addWidget(self._page_label)
        self._scroll_area.setWidget(scroll_content)

        layout.addWidget(self._scroll_area, stretch=1)

    def show_page(self, pixmap: QPixmap, page_index: int, page_count: int) -> None:
        self.setToolTip(f"Page {page_index + 1} of {page_count}")
        self._source_pixmap = pixmap
        self._update_displayed_page()
        self._request_higher_resolution_render_if_needed()
        self._page_label.setText("")

    def show_placeholder(self, message: str) -> None:
        self.setToolTip("")
        self._source_pixmap = QPixmap()
        self._page_label.setPixmap(QPixmap())
        self._page_label.setText(message)

    def current_source_width(self) -> int:
        return self._source_pixmap.width()

    def render_target_width(self) -> int:
        viewport_width = self._scroll_area.viewport().width()
        pixel_ratio = max(self.devicePixelRatioF(), 1.0)
        return max(
            self.MIN_RENDER_TARGET_WIDTH,
            int(viewport_width * self.RENDER_TARGET_MULTIPLIER * pixel_ratio),
        )

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._update_displayed_page()

    def eventFilter(self, watched, event):
        if watched is self._scroll_area.viewport() and event.type() == event.Type.Resize:
            self._update_displayed_page()
            self._request_higher_resolution_render_if_needed()
        return super().eventFilter(watched, event)

    def _update_displayed_page(self) -> None:
        if self._source_pixmap.isNull():
            return

        viewport_size = self._scroll_area.viewport().size()
        if not self._is_valid_size(viewport_size):
            return

        scaled_pixmap = self._source_pixmap.scaled(
            viewport_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._page_label.setPixmap(scaled_pixmap)

    def _request_higher_resolution_render_if_needed(self) -> None:
        if self._source_pixmap.isNull():
            return

        target_width = self.render_target_width()
        if self._source_pixmap.width() * self.RERENDER_TRIGGER_RATIO >= target_width:
            return

        self.higher_resolution_render_requested.emit(target_width)

    @staticmethod
    def _is_valid_size(size: QSize) -> bool:
        return size.width() > 0 and size.height() > 0
