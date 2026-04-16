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
        font-family: "Segoe UI Variable", "Segoe UI", "Trebuchet MS";
        font-size: 10.5pt;
    }

    QMenuBar {
        background: #171b20;
        color: #dfe6ef;
        border-bottom: 1px solid #242b34;
        padding: 2px 6px;
    }

    QMenuBar::item {
        background: transparent;
        border-radius: 6px;
        padding: 6px 10px;
    }

    QMenuBar::item:selected {
        background: #263343;
    }

    QMenu {
        background: #181d24;
        color: #e6ebf2;
        border: 1px solid #2b3441;
        padding: 6px;
    }

    QMenu::item {
        border-radius: 6px;
        padding: 7px 12px;
    }

    QMenu::item:selected {
        background: #2a3849;
    }

    QMenu::separator {
        height: 1px;
        background: #2f3742;
        margin: 6px 8px;
    }

    QToolBar {
        background: #171b20;
        border: none;
        spacing: 8px;
        padding: 8px 12px;
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
        border-radius: 9px;
        padding: 8px 11px;
        min-width: 78px;
    }

    QToolButton:hover {
        background: #2b3440;
        border-color: #3f4a59;
    }

    QToolButton:pressed {
        background: #313c49;
    }

    QToolButton:checked {
        background: #0b5f4e;
        color: #f2fff9;
        border: 2px solid #4de4b9;
    }

    QToolButton:checked:hover {
        background: #117a63;
        border-color: #7ff0ce;
    }

    QFrame#SidebarPlaceholder {
        background: qlineargradient(
            x1: 0,
            y1: 0,
            x2: 0,
            y2: 1,
            stop: 0 #1a2028,
            stop: 1 #171b20
        );
        border: 1px solid #272e37;
        border-radius: 12px;
    }

    QFrame#SidebarPlaceholder[collapsed="true"] {
        background: transparent;
        border: none;
    }

    QToolButton#InspectorCollapseButton {
        background: transparent;
        border: none;
        color: #c6cfdb;
        min-width: 24px;
        min-height: 24px;
    }

    QFrame#SidebarPlaceholder[collapsed="true"] QToolButton#InspectorCollapseButton {
        background: #242d39;
        border: 1px solid #33404f;
        border-radius: 8px;
    }

    QToolButton#InspectorCollapseButton:hover {
        background: #2b3847;
        border: 1px solid #46576a;
        border-radius: 8px;
    }

    QFrame#ViewerPanelContainer,
    QFrame#FilmstripPanel {
        background: transparent;
        border: none;
    }

    QFrame#FilmstripPanel {
        border-top: 1px solid #232a33;
        padding-top: 2px;
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

    QListWidget#ThumbnailList::item:hover {
        background: #222b37;
        border: 1px solid #354154;
    }

    QListWidget#ThumbnailList::item:selected {
        background: #0f253d;
        border: 2px solid #8bc5ff;
        color: #f4f9ff;
    }

    QScrollArea {
        border: none;
        background: transparent;
    }

    QComboBox,
    QLineEdit,
    QPushButton,
    QCheckBox {
        color: #e8eaed;
    }

    QComboBox,
    QLineEdit {
        background: #202833;
        border: 1px solid #303844;
        border-radius: 8px;
        padding: 6px 8px;
    }

    QPushButton {
        background: #242d39;
        border: 1px solid #33404f;
        border-radius: 8px;
        padding: 6px 10px;
    }

    QPushButton:hover {
        background: #2b3847;
        border-color: #46576a;
    }

    QStatusBar {
        background: #171b20;
        color: #9aa4b2;
        border-top: 1px solid #232a33;
    }
    """
