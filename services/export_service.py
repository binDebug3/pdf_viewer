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
        allow_overwrite: bool = False,
    ) -> list[Path]:
        if not page_groups:
            return []

        base_path = Path(base_output_path)
        self._validate_output_file(base_path)
        destination = base_path.parent
        destination.mkdir(parents=True, exist_ok=True)
        base_name = base_path.stem or session.source_path.stem or "split"
        export_paths = [
            destination / f"{base_name}_{index}.pdf" for index in range(1, len(page_groups) + 1)
        ]
        self._validate_overwrite(export_paths, allow_overwrite)
        exported_paths: list[Path] = []
        for group, path in zip(page_groups, export_paths):
            self._pdf_service.export_pages(self._pages_for_group(session, group), path)
            exported_paths.append(path)
        return exported_paths

    def export_session(
        self,
        session: DocumentSession,
        output_path: str | Path,
        allow_overwrite: bool = False,
    ) -> Path:
        if not session.pages:
            raise ValueError("Session has no pages to export.")

        destination = Path(output_path)
        self._validate_output_file(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        self._validate_overwrite([destination], allow_overwrite)
        return self._pdf_service.export_pages(session.pages, destination)

    @staticmethod
    def _pages_for_group(session: DocumentSession, indexes: list[int]):
        return [session.pages[index] for index in indexes]

    @staticmethod
    def _validate_output_file(path: Path) -> None:
        if path.suffix.lower() != ".pdf":
            raise ValueError("Export path must use a .pdf extension.")
        if path.exists() and path.is_dir():
            raise ValueError("Export path points to a directory.")

    @staticmethod
    def _validate_overwrite(paths: list[Path], allow_overwrite: bool) -> None:
        if allow_overwrite:
            return

        existing = [path for path in paths if path.exists()]
        if existing:
            raise FileExistsError(f"File already exists: {existing[0]}")
