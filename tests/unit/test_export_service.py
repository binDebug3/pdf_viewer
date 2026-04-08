from __future__ import annotations

from pathlib import Path

import fitz

from services.export_service import ExportService
from services.pdf_service import PdfService


def test_export_service_exports_single_group(tmp_path: Path) -> None:
    source_pdf = tmp_path / "source.pdf"
    _create_sample_pdf(source_pdf, 4)

    pdf_service = PdfService()
    export_service = ExportService(pdf_service)
    session = pdf_service.load_document(source_pdf)

    output = tmp_path / "split.pdf"
    exported_paths = export_service.export_groups(
        session,
        [[1, 3]],
        base_output_path=output,
    )

    expected_output = tmp_path / "split_1.pdf"
    assert exported_paths == [expected_output]
    exported_document = fitz.open(expected_output)
    assert exported_document.page_count == 2
    exported_document.close()


def test_export_service_exports_multiple_groups(tmp_path: Path) -> None:
    source_pdf = tmp_path / "source.pdf"
    _create_sample_pdf(source_pdf, 3)

    pdf_service = PdfService()
    export_service = ExportService(pdf_service)
    session = pdf_service.load_document(source_pdf)

    destination = tmp_path / "exports" / "session.pdf"
    exported_paths = export_service.export_groups(
        session,
        [[0], [2]],
        base_output_path=destination,
    )

    assert len(exported_paths) == 2
    assert all(path.exists() for path in exported_paths)
    assert exported_paths[0].name == "session_1.pdf"
    assert exported_paths[1].name == "session_2.pdf"


def _create_sample_pdf(file_path: Path, page_count: int) -> None:
    document = fitz.open()
    for index in range(page_count):
        page = document.new_page()
        page.insert_text((72, 72), f"Page {index + 1}")
    document.save(file_path)
    document.close()
