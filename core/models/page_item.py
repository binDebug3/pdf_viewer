from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PageItem:
    source_path: Path
    source_page_index: int
    rotation: int = 0

    @property
    def display_name(self) -> str:
        return f"Page {self.source_page_index + 1}"
