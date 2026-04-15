from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class SplitSpec:
    start_indexes: tuple[int, ...] = ()

    def normalized_starts(self, page_count: int) -> list[int]:
        if page_count <= 0:
            return []

        starts = {0}
        for index in self.start_indexes:
            if index <= 0:
                continue
            if index >= page_count:
                raise ValueError(f"Page index out of range for split start: {index + 1}")
            starts.add(index)
        return sorted(starts)

    mode: str = "current"
    custom_ranges: str = ""
    create_multiple_files: bool = False

    def selected_page_indexes(
        self,
        page_count: int,
        current_page_index: int = 0,
        selected_indexes: Iterable[int] | None = None,
    ) -> list[int]:
        if page_count <= 0:
            return []

        if self.start_indexes:
            starts = self.normalized_starts(page_count)
            return starts if self.create_multiple_files else list(range(page_count))

        safe_current = self._validated_page_index(current_page_index, page_count)
        selected = self._normalize_indexes(selected_indexes or [], page_count)

        if self.mode == "current":
            return [safe_current]
        if self.mode == "selected":
            return selected
        if self.mode == "odd":
            return [index for index in range(page_count) if (index + 1) % 2 == 1]
        if self.mode == "even":
            return [index for index in range(page_count) if (index + 1) % 2 == 0]
        if self.mode == "custom":
            return self._parse_custom_ranges(page_count)

        raise ValueError(f"Unsupported split mode: {self.mode}")

    def build_groups(self, page_count: int) -> list[list[int]]:
        starts = self.normalized_starts(page_count)
        if not starts:
            return []

        groups: list[list[int]] = []
        for position, start_index in enumerate(starts):
            end_index = starts[position + 1] if position + 1 < len(starts) else page_count
            groups.append(list(range(start_index, end_index)))
        return groups

    def build_output_groups(
        self,
        page_count: int,
        current_page_index: int = 0,
        selected_indexes: Iterable[int] | None = None,
    ) -> list[list[int]]:
        if page_count <= 0:
            return []

        if self.start_indexes:
            return self.build_groups(page_count)

        targets = self.selected_page_indexes(
            page_count=page_count,
            current_page_index=current_page_index,
            selected_indexes=selected_indexes,
        )
        if not targets:
            return []
        if self.create_multiple_files:
            return [[index] for index in targets]
        return [targets]

    def describe_output_groups(
        self,
        page_count: int,
        current_page_index: int = 0,
        selected_indexes: Iterable[int] | None = None,
    ) -> list[str]:
        descriptions: list[str] = []
        groups = self.build_output_groups(
            page_count=page_count,
            current_page_index=current_page_index,
            selected_indexes=selected_indexes,
        )
        for index, group in enumerate(groups, start=1):
            ranges = self._format_compact_ranges(group)
            page_label = "pages" if len(group) != 1 else "page"
            descriptions.append(f"{index}. {ranges} ({len(group)} {page_label})")
        return descriptions

    def can_split(
        self,
        page_count: int,
        current_page_index: int = 0,
        selected_indexes: Iterable[int] | None = None,
    ) -> bool:
        try:
            return bool(
                self.build_output_groups(
                    page_count=page_count,
                    current_page_index=current_page_index,
                    selected_indexes=selected_indexes,
                )
            )
        except ValueError:
            return False

    def validation_error(
        self,
        page_count: int,
        current_page_index: int = 0,
        selected_indexes: Iterable[int] | None = None,
    ) -> str | None:
        try:
            groups = self.build_output_groups(
                page_count=page_count,
                current_page_index=current_page_index,
                selected_indexes=selected_indexes,
            )
        except ValueError as error:
            return str(error)

        if groups:
            return None
        return "Split selection is empty. Choose a different split source."

    @staticmethod
    def _validated_page_index(page_index: int, page_count: int) -> int:
        if not 0 <= page_index < page_count:
            raise ValueError(f"Page index out of range: {page_index + 1}")
        return page_index

    @staticmethod
    def _normalize_indexes(indexes: Iterable[int], page_count: int) -> list[int]:
        normalized: set[int] = set()
        for index in indexes:
            if not 0 <= index < page_count:
                raise ValueError(f"Page index out of range: {index + 1}")
            normalized.add(index)
        return sorted(normalized)

    def _parse_custom_ranges(self, page_count: int) -> list[int]:
        text = self.custom_ranges.strip()
        if not text:
            return []

        pages: set[int] = set()
        for raw_part in text.split(","):
            part = raw_part.strip()
            if not part:
                continue

            if "-" in part:
                start_text, end_text = part.split("-", 1)
                start_page = self._parse_page_number(start_text)
                end_page = self._parse_page_number(end_text)
                if end_page < start_page:
                    raise ValueError(f"Invalid page range: {part}")
                for page_number in range(start_page, end_page + 1):
                    index = page_number - 1
                    if index >= page_count:
                        raise ValueError(
                            f"Page index out of range for custom split page: {page_number}"
                        )
                    pages.add(index)
                continue

            page_number = self._parse_page_number(part)
            index = page_number - 1
            if index >= page_count:
                raise ValueError(f"Page index out of range for custom split page: {page_number}")
            pages.add(index)

        return sorted(pages)

    @staticmethod
    def _parse_page_number(value: str) -> int:
        text = value.strip()
        if not text.isdigit():
            raise ValueError(f"Invalid page number in custom split ranges: {value}")
        page_number = int(text)
        if page_number <= 0:
            raise ValueError(f"Page numbers must be positive: {value}")
        return page_number

    @staticmethod
    def _format_compact_ranges(indexes: list[int]) -> str:
        if not indexes:
            return "no pages"

        ranges: list[str] = []
        start = indexes[0]
        end = indexes[0]
        for index in indexes[1:]:
            if index == end + 1:
                end = index
                continue

            ranges.append(SplitSpec._format_range(start, end))
            start = index
            end = index
        ranges.append(SplitSpec._format_range(start, end))
        return ", ".join(ranges)

    @staticmethod
    def _format_range(start_index: int, end_index: int) -> str:
        start_page = start_index + 1
        end_page = end_index + 1
        if start_page == end_page:
            return f"page {start_page}"
        return f"pages {start_page}-{end_page}"

    def describe_groups(self, page_count: int) -> list[str]:
        descriptions: list[str] = []
        for index, group in enumerate(self.build_groups(page_count), start=1):
            start_page = group[0] + 1
            end_page = group[-1] + 1
            if start_page == end_page:
                range_text = f"page {start_page}"
            else:
                range_text = f"pages {start_page}-{end_page}"
            page_label = "pages" if len(group) != 1 else "page"
            descriptions.append(f"{index}. {range_text} ({len(group)} {page_label})")
        return descriptions
