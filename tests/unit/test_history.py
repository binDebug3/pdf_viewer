from __future__ import annotations

from core.models.document_session import DocumentSession
from core.state.history import SessionHistory


def test_history_tracks_undo_redo_and_dirty_state() -> None:
    session = DocumentSession.from_page_count("example.pdf", 3)
    history = SessionHistory()
    history.reset(session)

    session.move_page(2, 0)
    history.record(session, "Reorder pages")

    assert history.can_undo
    assert not history.can_redo
    assert history.is_dirty

    undone_session, undo_step = history.undo()
    assert undone_session is not None
    assert undo_step is not None
    assert undo_step.label == "Reorder pages"
    assert not history.can_undo
    assert history.can_redo
    assert not history.is_dirty

    redone_session, redo_step = history.redo()
    assert redone_session is not None
    assert redo_step is not None
    assert redo_step.label == "Reorder pages"
    assert history.can_undo
    assert not history.can_redo
    assert history.is_dirty


def test_history_drops_redo_stack_when_recording_new_change() -> None:
    session = DocumentSession.from_page_count("example.pdf", 4)
    history = SessionHistory()
    history.reset(session)

    session.move_page(3, 0)
    history.record(session, "First reorder")

    history.undo()
    assert history.can_redo

    session.move_page(2, 1)
    history.record(session, "Second reorder")

    assert history.can_undo
    assert not history.can_redo


def test_history_mark_clean_resets_dirty_flag() -> None:
    session = DocumentSession.from_page_count("example.pdf", 2)
    history = SessionHistory()
    history.reset(session)

    session.append_document("other.pdf", 1)
    history.record(session, "Add PDF")
    assert history.is_dirty

    history.mark_clean()
    assert not history.is_dirty
