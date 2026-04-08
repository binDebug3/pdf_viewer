from __future__ import annotations

from PySide6.QtWidgets import QListWidget, QToolBar

from app.bootstrap import create_application, create_main_window


def test_main_window_smoke(qtbot) -> None:
    app = create_application()
    window = create_main_window()
    qtbot.addWidget(window)

    assert app.applicationName() == "PDF Viewer"
    assert window.windowTitle() == "PDF Viewer"
    assert window.minimumWidth() >= 860
    assert window.minimumHeight() >= 560
    assert window.findChild(QToolBar) is not None
    assert window.findChild(QListWidget) is not None
