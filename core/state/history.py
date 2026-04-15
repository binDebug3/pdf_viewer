from __future__ import annotations

from dataclasses import dataclass

from core.models.document_session import DocumentSession


@dataclass(frozen=True)
class HistoryStep:
    label: str
    from_index: int
    to_index: int


class SessionHistory:
    def __init__(self) -> None:
        self._states: list[DocumentSession] = []
        self._steps: list[str] = []
        self._cursor = 0
        self._clean_cursor = 0

    @property
    def can_undo(self) -> bool:
        return self._cursor > 0

    @property
    def can_redo(self) -> bool:
        return self._cursor < len(self._states) - 1

    @property
    def is_dirty(self) -> bool:
        return self._cursor != self._clean_cursor

    def reset(self, session: DocumentSession) -> None:
        self._states = [session.clone()]
        self._steps = []
        self._cursor = 0
        self._clean_cursor = 0

    def clear(self) -> None:
        self._states = []
        self._steps = []
        self._cursor = 0
        self._clean_cursor = 0

    def mark_clean(self) -> None:
        self._clean_cursor = self._cursor

    def record(self, session: DocumentSession, label: str) -> bool:
        if not self._states:
            self.reset(session)
            return False

        current = self._states[self._cursor]
        if current == session:
            return False

        if self.can_redo:
            self._states = self._states[: self._cursor + 1]
            self._steps = self._steps[: self._cursor]

        self._states.append(session.clone())
        self._steps.append(label)
        self._cursor += 1
        return True

    def undo(self) -> tuple[DocumentSession | None, HistoryStep | None]:
        if not self.can_undo:
            return None, None

        from_index = self._cursor
        to_index = self._cursor - 1
        label = self._steps[to_index]
        self._cursor = to_index
        step = HistoryStep(label=label, from_index=from_index, to_index=to_index)
        return self._states[self._cursor].clone(), step

    def redo(self) -> tuple[DocumentSession | None, HistoryStep | None]:
        if not self.can_redo:
            return None, None

        from_index = self._cursor
        to_index = self._cursor + 1
        label = self._steps[from_index]
        self._cursor = to_index
        step = HistoryStep(label=label, from_index=from_index, to_index=to_index)
        return self._states[self._cursor].clone(), step
