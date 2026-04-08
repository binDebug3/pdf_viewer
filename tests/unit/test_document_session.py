from __future__ import annotations

from core.models.document_session import DocumentSession


def test_document_session_tracks_page_count_and_selection() -> None:
    session = DocumentSession.from_page_count("example.pdf", 3)

    assert session.page_count == 3
    assert session.selected_page is not None
    assert session.selected_page.display_name == "Page 1"

    session.select_page(2)

    assert session.selected_page_index == 2
    assert session.selected_page is not None
    assert session.selected_page.display_name == "Page 3"
    assert session.source_count == 1
