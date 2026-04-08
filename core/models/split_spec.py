from __future__ import annotations

from dataclasses import dataclass


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

    def build_groups(self, page_count: int) -> list[list[int]]:
        starts = self.normalized_starts(page_count)
        if not starts:
            return []

        groups: list[list[int]] = []
        for position, start_index in enumerate(starts):
            end_index = starts[position + 1] if position + 1 < len(starts) else page_count
            groups.append(list(range(start_index, end_index)))
        return groups

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
