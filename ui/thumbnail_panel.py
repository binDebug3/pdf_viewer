from __future__ import annotations

from PySide6.QtCore import QPoint, Qt, Signal
from PySide6.QtGui import (
    QColor,
    QDragEnterEvent,
    QDragLeaveEvent,
    QDropEvent,
    QIcon,
    QMouseEvent,
    QPainter,
    QPen,
    QPixmap,
)
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
)


class FilmstripListWidget(QListWidget):
    reorder_requested = Signal(int, int)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._drag_source_row: int | None = None
        self._drop_row: int | None = None
        self._highlight_row: int | None = None
        self._document_breaks: set[int] = set()
        self._split_starts: set[int] = set()

    def set_document_breaks(self, document_breaks: set[int]) -> None:
        self._document_breaks = set(document_breaks)
        self.viewport().update()

    def set_split_starts(self, split_starts: set[int]) -> None:
        self._split_starts = set(split_starts)
        self.viewport().update()

    def startDrag(self, supported_actions) -> None:
        self._drag_source_row = self.currentRow()
        super().startDrag(supported_actions)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.source() is self:
            event.setDropAction(Qt.DropAction.CopyAction)
            event.accept()
            return
        super().dragEnterEvent(event)

    def dragMoveEvent(self, event) -> None:
        if event.source() is self:
            pos = event.position().toPoint()
            self._drop_row = self._drop_row_for_pos(pos)
            self._highlight_row = self._hover_row_for_pos(pos)
            self.viewport().update()
            event.setDropAction(Qt.DropAction.CopyAction)
            event.accept()
            return
        super().dragMoveEvent(event)

    def dragLeaveEvent(self, event: QDragLeaveEvent) -> None:
        self._drop_row = None
        self._highlight_row = None
        self.viewport().update()
        super().dragLeaveEvent(event)

    def dropEvent(self, event: QDropEvent) -> None:
        if event.source() is self and self._drag_source_row is not None:
            pos = event.position().toPoint()
            target_row = self._drop_row_for_pos(pos)
            final_row = self._final_row(self._drag_source_row, target_row)
            self._drop_row = target_row
            self._highlight_row = self._hover_row_for_pos(pos)
            self.viewport().update()
            event.setDropAction(Qt.DropAction.CopyAction)
            event.accept()
            if final_row != self._drag_source_row:
                self.reorder_requested.emit(self._drag_source_row, final_row)
            self._drag_source_row = None
            return

        super().dropEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self._drop_row = None
        self._highlight_row = None
        self.viewport().update()
        super().mousePressEvent(event)

    def paintEvent(self, event) -> None:
        super().paintEvent(event)

        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)

        for break_row in sorted(self._document_breaks):
            if 0 < break_row < self.count():
                x_pos = self._separator_x(break_row)
                height = self.viewport().height()
                divider_left = x_pos - 7
                divider_height = max(0, height - 8)
                painter.fillRect(divider_left, 4, 14, divider_height, QColor("#fff4cc"))
                painter.fillRect(
                    divider_left + 1,
                    5,
                    12,
                    max(0, divider_height - 2),
                    QColor("#ff9f1c"),
                )

        marker_color = QColor("#51c7c2")
        badge_pen = QPen(QColor("#0d1f2b"))
        badge_pen.setWidth(1)
        for badge_index, split_row in enumerate(sorted(self._split_starts), start=1):
            if 0 <= split_row < self.count():
                rect = self.visualItemRect(self.item(split_row)).adjusted(4, 3, -4, -4)
                painter.fillRect(rect.left(), rect.top(), rect.width(), 5, marker_color)
                badge_rect = rect.adjusted(rect.width() - 20, 8, -2, -rect.height() + 26)
                painter.setPen(badge_pen)
                painter.setBrush(marker_color)
                painter.drawEllipse(badge_rect)
                painter.drawText(badge_rect, Qt.AlignmentFlag.AlignCenter, str(badge_index))

        current_row = self.currentRow()
        if 0 <= current_row < self.count():
            current_pen = QPen(QColor("#ffd166"))
            current_pen.setWidth(3)
            painter.setPen(current_pen)
            current_rect = self.visualItemRect(self.item(current_row)).adjusted(0, 0, -1, -1)
            painter.drawRect(current_rect)

        if self._highlight_row is not None and 0 <= self._highlight_row < self.count():
            highlight_pen = QPen(QColor("#78b7ff"))
            highlight_pen.setWidth(3)
            painter.setPen(highlight_pen)
            rect = self.visualItemRect(self.item(self._highlight_row)).adjusted(1, 1, -1, -1)
            painter.drawRect(rect)

        if self._drop_row is not None:
            indicator_pen = QPen(QColor("#78b7ff"))
            indicator_pen.setWidth(5)
            painter.setPen(indicator_pen)

            x_pos = self._indicator_x(self._drop_row)
            height = self.viewport().height()
            painter.drawLine(x_pos, 8, x_pos, max(8, height - 8))

    def _drop_row_for_pos(self, pos: QPoint) -> int:
        item = self.itemAt(pos)
        if item is None:
            if self.count() == 0:
                return 0

            last_rect = self.visualItemRect(self.item(self.count() - 1))
            if pos.x() > last_rect.center().x():
                return self.count()
            return self.count() - 1

        row = self.row(item)
        rect = self.visualItemRect(item)
        if pos.x() > rect.center().x():
            return row + 1
        return row

    def _hover_row_for_pos(self, pos: QPoint) -> int | None:
        item = self.itemAt(pos)
        if item is None:
            if self.count() == 0:
                return None
            return self.count() - 1
        return self.row(item)

    def _indicator_x(self, drop_row: int) -> int:
        if self.count() == 0:
            return 8
        if drop_row <= 0:
            rect = self.visualItemRect(self.item(0))
            return rect.left() - 6
        if drop_row >= self.count():
            rect = self.visualItemRect(self.item(self.count() - 1))
            return rect.right() + 6

        previous_rect = self.visualItemRect(self.item(drop_row - 1))
        current_rect = self.visualItemRect(self.item(drop_row))
        return (previous_rect.right() + current_rect.left()) // 2

    def _separator_x(self, break_row: int) -> int:
        previous_rect = self.visualItemRect(self.item(break_row - 1))
        current_rect = self.visualItemRect(self.item(break_row))
        return (previous_rect.right() + current_rect.left()) // 2

    @staticmethod
    def _final_row(source_row: int, target_row: int) -> int:
        if source_row < target_row:
            return max(0, target_row - 1)
        return target_row


class ThumbnailPanel(QFrame):
    page_selected = Signal(int)
    page_clicked = Signal(int)
    page_reordered = Signal(int, int)
    selection_changed = Signal(list)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("FilmstripPanel")
        self.setFixedHeight(98)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._list = FilmstripListWidget(self)
        self._list.setObjectName("ThumbnailList")
        self._list.setViewMode(QListWidget.ViewMode.IconMode)
        self._list.setFlow(QListWidget.Flow.LeftToRight)
        self._list.setMovement(QListWidget.Movement.Static)
        self._list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self._list.setWrapping(False)
        self._list.setIconSize(QPixmap(59, 77).size())
        self._list.setGridSize(QPixmap(68, 88).size())
        self._list.setSpacing(2)
        self._list.setDragEnabled(True)
        self._list.setAcceptDrops(True)
        self._list.viewport().setAcceptDrops(True)
        self._list.setDropIndicatorShown(False)
        self._list.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self._list.setDragDropOverwriteMode(False)
        self._list.setDefaultDropAction(Qt.DropAction.MoveAction)
        self._list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self._list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._list.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self._list.setWordWrap(True)
        self._list.setUniformItemSizes(False)
        self._list.currentRowChanged.connect(self._emit_selection)
        self._list.itemClicked.connect(self._emit_click)
        self._list.itemSelectionChanged.connect(self._emit_selection_change)
        self._list.reorder_requested.connect(self.page_reordered.emit)

        layout.addWidget(self._list, stretch=1)

    def set_pages(
        self,
        thumbnails: list[QPixmap],
        document_breaks: set[int] | None = None,
    ) -> None:
        breaks = document_breaks or set()
        self._list.clear()
        self._list.set_document_breaks(breaks)
        for index, thumbnail in enumerate(thumbnails):
            item = QListWidgetItem(QIcon(thumbnail), f"{index + 1}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setData(Qt.ItemDataRole.UserRole, index)
            flags = item.flags() | Qt.ItemFlag.ItemIsDragEnabled
            flags |= Qt.ItemFlag.ItemIsDropEnabled
            item.setFlags(flags)
            self._list.addItem(item)

        if thumbnails:
            self._list.setCurrentRow(0)
            self._emit_selection_change()

    def set_current_page(self, index: int) -> None:
        if 0 <= index < self._list.count() and self._list.currentRow() != index:
            self._list.setCurrentRow(index)

    def clear_pages(self) -> None:
        self._list.clear()
        self._list.set_document_breaks(set())
        self._list.set_split_starts(set())
        self.selection_changed.emit([])

    def selected_rows(self) -> list[int]:
        return sorted(item.data(Qt.ItemDataRole.UserRole) for item in self._list.selectedItems())

    def set_selected_pages(self, indexes: list[int]) -> None:
        selected = set(indexes)
        self._list.blockSignals(True)
        for row in range(self._list.count()):
            item = self._list.item(row)
            item.setSelected(row in selected)
        self._list.blockSignals(False)
        self._emit_selection_change()

    def set_split_starts(self, indexes: set[int]) -> None:
        self._list.set_split_starts(indexes)

    def _emit_selection(self, row: int) -> None:
        if row >= 0:
            self.page_selected.emit(row)

    def _emit_click(self, item: QListWidgetItem) -> None:
        row = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(row, int):
            self.page_clicked.emit(row)

    def _emit_selection_change(self) -> None:
        self.selection_changed.emit(self.selected_rows())
