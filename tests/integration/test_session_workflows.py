"""Integration tests for session editing workflows and history behavior."""

from __future__ import annotations

from pathlib import Path

import fitz
import pytest

from app.bootstrap import create_application
from core.state.history import SessionHistory
from services.export_service import ExportService
from services.pdf_service import PdfService
from tests.fixtures.pdf_factory import create_multi_page_pdf


@pytest.fixture(scope="module", autouse=True)
def _application() -> None:
    """Initialize Qt once for tests that create pixmaps."""
    create_application()


def test_join_reorder_delete_duplicate_and_history(tmp_path: Path) -> None:
    """Validate core page operations with undo/redo session transitions."""
    first_pdf = create_multi_page_pdf(tmp_path / "first.pdf", page_count=3)
    second_pdf = create_multi_page_pdf(tmp_path / "second.pdf", page_count=2)

    pdf_service = PdfService()
    history = SessionHistory()

    session = pdf_service.load_document(first_pdf)
    history.reset(session)

    before_add = session.clone()
    session.append_document(second_pdf, pdf_service.get_page_count(second_pdf))
    assert history.record(session, "Add PDF")
    assert session.page_count == 5
    assert before_add.page_count == 3

    before_move = session.clone()
    selected_index = session.move_page(source_index=4, destination_index=1)
    assert history.record(session, "Reorder pages")
    assert selected_index == 0
    assert session.selected_page_index == 0
    assert session.page_count == 5
    assert before_move.page_count == 5

    before_duplicate = session.clone()
    inserted = session.duplicate_pages([0, 2])
    assert history.record(session, "Duplicate pages")
    assert inserted == [1, 4]
    assert session.page_count == 7
    assert before_duplicate.page_count == 5

    before_delete = session.clone()
    session.select_page(3)
    selected_after_delete = session.delete_pages([1, 3])
    assert history.record(session, "Delete pages")
    assert selected_after_delete is not None
    assert session.page_count == 5
    assert before_delete.page_count == 7
    assert history.can_undo

    session_after_delete = session.clone()
    undone, undo_step = history.undo()
    assert undo_step is not None
    assert undo_step.label == "Delete pages"
    assert undone is not None
    assert undone.page_count == 7

    redone, redo_step = history.redo()
    assert redo_step is not None
    assert redo_step.label == "Delete pages"
    assert redone is not None
    assert redone.page_count == session_after_delete.page_count

    pdf_service.close_all()


def test_save_as_export_reflects_reordered_session(tmp_path: Path) -> None:
    """Ensure export writes the current session state and page ordering."""
    source_pdf = create_multi_page_pdf(tmp_path / "source.pdf", page_count=4)

    pdf_service = PdfService()
    export_service = ExportService(pdf_service)
    session = pdf_service.load_document(source_pdf)
    session.move_page(source_index=3, destination_index=0)

    output = tmp_path / "exported.pdf"
    exported_path = export_service.export_session(session, output)

    assert exported_path == output
    exported_doc = fitz.open(exported_path)
    try:
        assert exported_doc.page_count == 4
    finally:
        exported_doc.close()
        pdf_service.close_all()
