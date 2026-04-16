from __future__ import annotations

from pathlib import Path

import fitz
from PySide6.QtGui import QImage, QPixmap

from core.models.document_session import DocumentSession
from core.models.page_item import PageItem


class PdfService:
    MIN_RENDER_SCALE = 0.2
    MAX_RENDER_SCALE = 8.0

    def __init__(self) -> None:
        self._documents: dict[str, fitz.Document] = {}

    def load_document(self, file_path: str | Path) -> DocumentSession:
        document = self._get_document(file_path)
        return DocumentSession.from_page_count(file_path, document.page_count)

    def get_page_count(self, file_path: str | Path) -> int:
        return self._get_document(file_path).page_count

    def render_page(self, file_path: str | Path, page_index: int, max_width: int = 920) -> QPixmap:
        document = self._get_document(file_path)
        page = document.load_page(page_index)
        scale = self._scale_for_max_width(page.rect.width, max_width)
        pixmap = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
        return self._to_qpixmap(pixmap)

    def render_thumbnail(
        self,
        file_path: str | Path,
        page_index: int,
        max_edge: int = 140,
    ) -> QPixmap:
        document = self._get_document(file_path)
        page = document.load_page(page_index)
        width_scale = max_edge / max(page.rect.width, 1)
        height_scale = max_edge / max(page.rect.height, 1)
        scale = max(min(width_scale, height_scale), 0.1)
        pixmap = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
        return self._to_qpixmap(pixmap)

    def close_all(self) -> None:
        for document in self._documents.values():
            document.close()
        self._documents.clear()

    def export_pages(self, pages: list[PageItem], output_path: str | Path) -> Path:
        destination = Path(output_path)
        export_document = fitz.open()
        try:
            for page in pages:
                source_document = self._get_document(page.source_path)
                export_document.insert_pdf(
                    source_document,
                    from_page=page.source_page_index,
                    to_page=page.source_page_index,
                )
                if page.rotation % 360 != 0:
                    inserted_page = export_document.load_page(export_document.page_count - 1)
                    inserted_page.set_rotation(page.rotation % 360)
            export_document.save(destination)
        finally:
            export_document.close()
        return destination

    def _get_document(self, file_path: str | Path) -> fitz.Document:
        resolved_path = str(Path(file_path).resolve())
        if resolved_path not in self._documents:
            self._documents[resolved_path] = fitz.open(resolved_path)
        return self._documents[resolved_path]

    @staticmethod
    def _scale_for_max_width(page_width: float, max_width: int) -> float:
        raw_scale = max_width / max(page_width, 1)
        return max(min(raw_scale, PdfService.MAX_RENDER_SCALE), PdfService.MIN_RENDER_SCALE)

    @staticmethod
    def _to_qpixmap(pixmap: fitz.Pixmap) -> QPixmap:
        image_format = (
            QImage.Format.Format_RGBA8888 if pixmap.alpha else QImage.Format.Format_RGB888
        )
        image = QImage(pixmap.samples, pixmap.width, pixmap.height, pixmap.stride, image_format)
        return QPixmap.fromImage(image.copy())
