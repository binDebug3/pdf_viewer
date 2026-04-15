"""UI-level tests for stable mouse-first interactions."""

from __future__ import annotations

from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLineEdit

from ui.inspector_panel import InspectorPanel
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
