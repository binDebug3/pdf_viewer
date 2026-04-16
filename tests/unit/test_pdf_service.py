from __future__ import annotations

from pathlib import Path

import fitz

from app.bootstrap import create_application
from core.models.page_item import PageItem
from services.pdf_service import PdfService


def test_pdf_service_loads_and_renders_pdf(tmp_path: Path) -> None:
    create_application()
    file_path = tmp_path / "sample.pdf"
    _create_sample_pdf(file_path)

    service = PdfService()
    session = service.load_document(file_path)
    thumbnail = service.render_thumbnail(file_path, 0)
    page = service.render_page(file_path, 0)

    assert session.page_count == 2
    assert thumbnail.width() > 0
    assert thumbnail.height() > 0
    assert page.width() > 0
    assert page.height() > 0

    service.close_all()


def test_pdf_service_preserves_page_rotation_on_export(tmp_path: Path) -> None:
    create_application()
    file_path = tmp_path / "sample.pdf"
    _create_sample_pdf(file_path)

    service = PdfService()
    output_path = tmp_path / "rotated.pdf"
    pages = [PageItem(source_path=file_path, source_page_index=0, rotation=90)]

    service.export_pages(pages, output_path)

    exported_document = fitz.open(output_path)
    try:
        assert exported_document.page_count == 1
        assert exported_document[0].rotation == 90
    finally:
        exported_document.close()
        service.close_all()


def test_render_page_respects_large_target_width(tmp_path: Path) -> None:
    create_application()
    file_path = tmp_path / "sample.pdf"
    _create_sample_pdf(file_path)

    service = PdfService()
    rendered_page = service.render_page(file_path, 0, max_width=3200)

    assert rendered_page.width() >= 3000

    service.close_all()


def _create_sample_pdf(file_path: Path) -> None:
    document = fitz.open()
    for index in range(2):
        page = document.new_page()
        page.insert_text((72, 72), f"Page {index + 1}")
    document.save(file_path)
    document.close()
