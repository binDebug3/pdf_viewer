from __future__ import annotations

from pathlib import Path

from core.models.document_session import DocumentSession
from services.pdf_service import PdfService


class ExportService:
    def __init__(self, pdf_service: PdfService) -> None:
        self._pdf_service = pdf_service

    def export_groups(
        self,
        session: DocumentSession,
        page_groups: list[list[int]],
        base_output_path: str | Path,
    ) -> list[Path]:
        if not page_groups:
            return []

        base_path = Path(base_output_path)
        destination = base_path.parent
        destination.mkdir(parents=True, exist_ok=True)
        base_name = base_path.stem or session.source_path.stem or "split"
        exported_paths: list[Path] = []
        for index, group in enumerate(page_groups, start=1):
            path = destination / f"{base_name}_{index}.pdf"
            self._pdf_service.export_pages(self._pages_for_group(session, group), path)
            exported_paths.append(path)
        return exported_paths

    @staticmethod
    def _pages_for_group(session: DocumentSession, indexes: list[int]):
        return [session.pages[index] for index in indexes]
