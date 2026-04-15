"""Integration tests for split planning and export alignment."""

from __future__ import annotations

from pathlib import Path

import fitz
import pytest

from app.bootstrap import create_application
from core.models.page_item import PageItem
from core.models.split_spec import SplitSpec
from services.export_service import ExportService
from services.pdf_service import PdfService
from tests.fixtures.pdf_factory import create_mixed_size_pdf, create_split_candidate_pdf


@pytest.fixture(scope="module", autouse=True)
def _application() -> None:
    """Initialize Qt for rendering and pixmap conversion paths."""
    create_application()


def test_split_selection_matches_exported_groups(tmp_path: Path) -> None:
    """Verify split groups and resulting PDFs stay aligned by page count."""
    source_pdf = create_split_candidate_pdf(tmp_path / "split_source.pdf")

    pdf_service = PdfService()
    export_service = ExportService(pdf_service)
    session = pdf_service.load_document(source_pdf)

    split_spec = SplitSpec(mode="selected", create_multiple_files=True)
    groups = split_spec.build_output_groups(
        page_count=session.page_count,
        current_page_index=0,
        selected_indexes=[0, 3, 5],
    )

    exported = export_service.export_groups(
        session=session,
        page_groups=groups,
        base_output_path=tmp_path / "selected_split.pdf",
    )

    assert len(groups) == 3
    assert len(exported) == 3
    for path in exported:
        document = fitz.open(path)
        try:
            assert document.page_count == 1
        finally:
            document.close()

    pdf_service.close_all()


def test_custom_split_ranges_produce_expected_group_sizes(tmp_path: Path) -> None:
    """Validate custom range parsing and export page totals for split mode."""
    source_pdf = create_split_candidate_pdf(tmp_path / "range_source.pdf")

    pdf_service = PdfService()
    export_service = ExportService(pdf_service)
    session = pdf_service.load_document(source_pdf)

    split_spec = SplitSpec(mode="custom", custom_ranges="1,3-4,7", create_multiple_files=False)
    groups = split_spec.build_output_groups(page_count=session.page_count)
    exported = export_service.export_groups(
        session=session,
        page_groups=groups,
        base_output_path=tmp_path / "custom_split.pdf",
    )

    assert groups == [[0, 2, 3, 6]]
    assert len(exported) == 1

    exported_doc = fitz.open(exported[0])
    try:
        assert exported_doc.page_count == 4
    finally:
        exported_doc.close()
        pdf_service.close_all()


def test_export_preserves_rotation_metadata(tmp_path: Path) -> None:
    """Ensure page-level rotation metadata survives export."""
    source_pdf = create_mixed_size_pdf(tmp_path / "mixed.pdf")

    pdf_service = PdfService()
    pages = [PageItem(source_path=source_pdf, source_page_index=2, rotation=180)]

    output_path = tmp_path / "rotated_export.pdf"
    pdf_service.export_pages(pages, output_path)

    exported_document = fitz.open(output_path)
    try:
        assert exported_document.page_count == 1
        assert exported_document[0].rotation == 180
    finally:
        exported_document.close()
        pdf_service.close_all()
