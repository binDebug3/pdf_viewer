from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from core.models.page_item import PageItem


@dataclass
class DocumentSession:
    source_path: Path
    pages: list[PageItem] = field(default_factory=list)
    selected_page_index: int = 0

    @classmethod
    def from_page_count(cls, file_path: str | Path, page_count: int) -> "DocumentSession":
        path = Path(file_path)
        pages = [PageItem(source_path=path, source_page_index=index) for index in range(page_count)]
        return cls(source_path=path, pages=pages)

    @property
    def page_count(self) -> int:
        return len(self.pages)

    @property
    def source_paths(self) -> list[Path]:
        return list(dict.fromkeys(page.source_path for page in self.pages))

    @property
    def source_count(self) -> int:
        return len(self.source_paths)

    @property
    def selected_page(self) -> PageItem | None:
        if not self.pages:
            return None
        return self.pages[self.selected_page_index]

    def select_page(self, index: int) -> None:
        if not 0 <= index < self.page_count:
            raise IndexError(f"Page index out of range: {index}")
        self.selected_page_index = index

    def append_document(self, file_path: str | Path, page_count: int) -> None:
        path = Path(file_path)
        self.pages.extend(
            PageItem(source_path=path, source_page_index=index) for index in range(page_count)
        )

    def move_page(self, source_index: int, destination_index: int) -> int:
        if not 0 <= source_index < self.page_count:
            raise IndexError(f"Page index out of range: {source_index}")
        if not 0 <= destination_index < self.page_count:
            raise IndexError(f"Page index out of range: {destination_index}")

        page = self.pages.pop(source_index)
        self.pages.insert(destination_index, page)

        if self.selected_page_index == source_index:
            self.selected_page_index = destination_index
        elif source_index < self.selected_page_index <= destination_index:
            self.selected_page_index -= 1
        elif destination_index <= self.selected_page_index < source_index:
            self.selected_page_index += 1

        return self.selected_page_index

    def delete_pages(self, indexes: list[int]) -> int | None:
        unique_indexes = sorted(set(indexes))
        if not unique_indexes:
            return self.selected_page_index if self.pages else None

        for index in reversed(unique_indexes):
            if not 0 <= index < self.page_count:
                raise IndexError(f"Page index out of range: {index}")
            self.pages.pop(index)

        if not self.pages:
            self.selected_page_index = 0
            return None

        removed_before_selection = sum(
            1 for index in unique_indexes if index < self.selected_page_index
        )
        if self.selected_page_index in unique_indexes:
            candidate_index = min(unique_indexes[0], len(self.pages) - 1)
        else:
            candidate_index = self.selected_page_index - removed_before_selection

        self.selected_page_index = max(0, min(candidate_index, len(self.pages) - 1))
        return self.selected_page_index

    def duplicate_pages(self, indexes: list[int]) -> list[int]:
        unique_indexes = sorted(set(indexes))
        if not unique_indexes:
            return []

        inserted_indexes: list[int] = []
        offset = 0
        for index in unique_indexes:
            if not 0 <= index < self.page_count:
                raise IndexError(f"Page index out of range: {index}")

            insertion_index = index + 1 + offset
            duplicated_page = self.pages[index + offset]
            self.pages.insert(insertion_index, duplicated_page)
            inserted_indexes.append(insertion_index)
            offset += 1

        self.selected_page_index = inserted_indexes[0]
        return inserted_indexes
