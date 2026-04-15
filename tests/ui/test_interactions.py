"""UI-level tests for stable mouse-first interactions."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLineEdit

from core.models.document_session import DocumentSession
from tests.fixtures.pdf_factory import create_multi_page_pdf
from ui.inspector_panel import InspectorPanel
from ui.main_window import MainWindow
from ui.thumbnail_panel import ThumbnailPanel


def test_thumbnail_panel_selection_sync(qtbot) -> None:
    """Selected rows should stay synchronized with panel selection APIs."""
    panel = ThumbnailPanel()
    qtbot.addWidget(panel)

    panel.set_pages([QPixmap(60, 80), QPixmap(60, 80), QPixmap(60, 80)])
    panel.set_selected_pages([0, 2])

    assert panel.selected_rows() == [0, 2]

    panel.set_current_page(1)
    assert panel._list.currentRow() == 1


def test_inspector_split_controls_toggle_custom_ranges_visibility(qtbot) -> None:
    """Custom range input should show only for custom split mode."""
    panel = InspectorPanel()
    qtbot.addWidget(panel)

    custom_input = panel.findChild(QLineEdit)
    assert custom_input is not None

    panel.set_split_controls(mode="selected", custom_ranges="", create_multiple_files=False)
    assert custom_input.isHidden() is True

    panel.set_split_controls(mode="custom", custom_ranges="1-3", create_multiple_files=True)
    assert custom_input.isHidden() is False


def test_inspector_emits_split_options_on_apply(qtbot) -> None:
    """Apply should emit current split options for the parent workflow."""
    panel = InspectorPanel()
    qtbot.addWidget(panel)
    panel.set_document_state(
        file_path="example.pdf",
        page_count=4,
        selected_page_index=1,
        split_mode_active=True,
    )

    with qtbot.waitSignal(panel.split_options_changed, timeout=1000) as signal:
        panel._split_mode.setCurrentIndex(panel._split_mode.findData("custom"))

    assert signal.args[0] == "custom"


def test_split_mode_click_toggles_selected_page(qtbot, monkeypatch) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    monkeypatch.setattr(window, "_confirm_discard_unsaved_changes", lambda: True)

    session = DocumentSession.from_page_count("example.pdf", 3)
    window._session = session
    window._pdf_service.render_thumbnail = lambda *_args, **_kwargs: QPixmap(60, 80)
    window._pdf_service.render_page = lambda *_args, **_kwargs: QPixmap(640, 800)
    window._refresh_thumbnails(preserve_selection=False)
    window._select_page(0)
    window._enter_split_mode()

    window._handle_page_clicked(1)
    assert window._selected_page_indexes == [1]

    window._handle_page_clicked(1)
    assert window._selected_page_indexes == []


def test_rotate_action_rotates_selected_pages(qtbot, monkeypatch) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    monkeypatch.setattr(window, "_confirm_discard_unsaved_changes", lambda: True)

    session = DocumentSession.from_page_count("example.pdf", 3)
    window._session = session
    window._pdf_service.render_thumbnail = lambda *_args, **_kwargs: QPixmap(60, 80)
    window._pdf_service.render_page = lambda *_args, **_kwargs: QPixmap(640, 800)
    window._refresh_thumbnails(preserve_selection=False)
    window._selected_page_indexes = [0, 2]

    window._handle_toolbar_action("rotate")

    assert window._session.pages[0].rotation == 90
    assert window._session.pages[1].rotation == 0
    assert window._session.pages[2].rotation == 90


def test_join_action_appends_multiple_documents(qtbot, monkeypatch, tmp_path: Path) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    monkeypatch.setattr(window, "_confirm_discard_unsaved_changes", lambda: True)

    first_pdf = create_multi_page_pdf(tmp_path / "first.pdf", page_count=2)
    second_pdf = create_multi_page_pdf(tmp_path / "second.pdf", page_count=3)

    from ui import main_window as main_window_module

    monkeypatch.setattr(
        main_window_module.QFileDialog,
        "getOpenFileNames",
        staticmethod(
            lambda *_args, **_kwargs: (
                [str(first_pdf), str(second_pdf)],
                "PDF Files (*.pdf)",
            )
        ),
    )

    window._handle_toolbar_action("join")

    assert window._session is not None
    assert window._session.page_count == 5
    assert window._session.source_count == 2
