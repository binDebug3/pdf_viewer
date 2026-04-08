from __future__ import annotations

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow


def create_application() -> QApplication:
    app = QApplication.instance() or QApplication([])
    app.setApplicationName("PDF Viewer")
    app.setApplicationDisplayName("PDF Viewer")
    app.setOrganizationName("pdf_viewer")
    app.setStyle("Fusion")
    app.setPalette(_build_palette())
    app.setStyleSheet(_build_stylesheet())
    return app


def create_main_window() -> MainWindow:
    return MainWindow()


def _build_palette() -> QPalette:
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#121417"))
    palette.setColor(QPalette.WindowText, QColor("#e8eaed"))
    palette.setColor(QPalette.Base, QColor("#1b1f24"))
    palette.setColor(QPalette.AlternateBase, QColor("#232931"))
    palette.setColor(QPalette.ToolTipBase, QColor("#1f242b"))
    palette.setColor(QPalette.ToolTipText, QColor("#f3f4f6"))
    palette.setColor(QPalette.Text, QColor("#e8eaed"))
    palette.setColor(QPalette.Button, QColor("#232931"))
    palette.setColor(QPalette.ButtonText, QColor("#e8eaed"))
    palette.setColor(QPalette.Highlight, QColor("#4b7bec"))
    palette.setColor(QPalette.HighlightedText, QColor("#f8fafc"))
    return palette


def _build_stylesheet() -> str:
    return """
    QMainWindow {
        background: #121417;
    }

    QToolBar {
        background: #171b20;
        border: none;
        spacing: 6px;
        padding: 6px 10px;
    }

    QToolBar::separator {
        width: 1px;
        background: #2f3742;
        margin: 6px 8px;
    }

    QToolButton {
        background: #232931;
        color: #e8eaed;
        border: 1px solid #303844;
        border-radius: 8px;
        padding: 7px 10px;
    }

    QToolButton:hover {
        background: #2b3440;
        border-color: #3f4a59;
    }

    QToolButton:pressed {
        background: #313c49;
    }

    QFrame#SidebarPlaceholder {
        background: #171b20;
        border: 1px solid #272e37;
        border-radius: 12px;
    }

    QFrame#ViewerPanelContainer,
    QFrame#FilmstripPanel {
        background: transparent;
        border: none;
    }

    QLabel#SectionTitle {
        color: #f3f4f6;
        font-size: 13px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }

    QLabel#MutedText {
        color: #98a2b3;
        font-size: 12px;
    }

    QLabel#PageCanvas {
        background: transparent;
        border: none;
        padding: 0;
    }

    QListWidget#ThumbnailList {
        background: transparent;
        border: none;
        outline: none;
        padding: 0;
    }

    QListWidget#ThumbnailList::item {
        color: #d7dce3;
        border-radius: 6px;
        padding: 4px;
        margin: 1px;
    }

    QListWidget#ThumbnailList::item:selected {
        background: #243247;
        border: 1px solid #4b7bec;
    }

    QScrollArea {
        border: none;
        background: transparent;
    }

    QStatusBar {
        background: #171b20;
        color: #9aa4b2;
        border-top: 1px solid #232a33;
    }
    """
