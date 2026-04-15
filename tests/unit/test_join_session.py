from __future__ import annotations

from core.models.document_session import DocumentSession


def test_document_session_can_append_second_document() -> None:
    session = DocumentSession.from_page_count("first.pdf", 2)

    session.append_document("second.pdf", 3)

    assert session.page_count == 5
    assert session.source_count == 2
    assert session.pages[2].source_page_index == 0
    assert session.pages[2].source_path.name == "second.pdf"


def test_document_session_reorders_pages_and_preserves_selection() -> None:
    session = DocumentSession.from_page_count("first.pdf", 3)
    session.append_document("second.pdf", 2)
    session.select_page(4)

    selected_index = session.move_page(4, 1)

    assert selected_index == 1
    assert session.selected_page_index == 1
    assert session.pages[1].source_path.name == "second.pdf"
    assert session.pages[1].source_page_index == 1


def test_document_session_can_delete_selected_pages() -> None:
    session = DocumentSession.from_page_count("first.pdf", 4)
    session.select_page(2)

    selected_index = session.delete_pages([1, 2])

    assert session.page_count == 2
    assert selected_index == 1
    assert session.selected_page_index == 1
    assert session.pages[0].source_page_index == 0
    assert session.pages[1].source_page_index == 3


def test_document_session_can_duplicate_selected_pages() -> None:
    session = DocumentSession.from_page_count("first.pdf", 3)

    inserted_indexes = session.duplicate_pages([0, 2])

    assert session.page_count == 5
    assert inserted_indexes == [1, 4]
    assert session.selected_page_index == 1
    assert session.pages[1].source_page_index == 0
    assert session.pages[4].source_page_index == 2


def test_document_session_rotates_selected_pages_clockwise() -> None:
    session = DocumentSession.from_page_count("first.pdf", 3)

    rotated_indexes = session.rotate_pages([0, 2], degrees=90)

    assert rotated_indexes == [0, 2]
    assert session.pages[0].rotation == 90
    assert session.pages[1].rotation == 0
    assert session.pages[2].rotation == 90
    assert session.selected_page_index == 0
