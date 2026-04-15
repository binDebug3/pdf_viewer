"""Build deterministic PDF samples for automated tests."""

from __future__ import annotations

from pathlib import Path

import fitz

PAGE_TEXT_POSITION = (72, 72)


def create_sample_pdf(file_path: Path, page_sizes: list[tuple[float, float]]) -> Path:
    """Create a sample PDF with predictable text labels on each page.

    Args:
        file_path: Output path for the generated PDF.
        page_sizes: Ordered page sizes as ``(width, height)`` points.

    Returns:
        The output path that was written.
    """
    document = fitz.open()
    try:
        for index, (width, height) in enumerate(page_sizes, start=1):
            page = document.new_page(width=width, height=height)
            page.insert_text(PAGE_TEXT_POSITION, f"Sample page {index}")
        document.save(file_path)
    finally:
        document.close()
    return file_path


def create_single_page_pdf(file_path: Path) -> Path:
    """Create a single-page PDF."""
    return create_sample_pdf(file_path, [(595, 842)])


def create_multi_page_pdf(file_path: Path, page_count: int = 5) -> Path:
    """Create a same-size multi-page PDF.

    Args:
        file_path: Output path for the generated PDF.
        page_count: Total pages to include.

    Returns:
        The output path that was written.
    """
    return create_sample_pdf(file_path, [(595, 842) for _ in range(page_count)])


def create_mixed_size_pdf(file_path: Path) -> Path:
    """Create a mixed-size PDF to exercise rendering and export paths."""
    return create_sample_pdf(file_path, [(595, 842), (842, 595), (612, 1008), (420, 594)])


def create_rotated_source_pdf(file_path: Path) -> Path:
    """Create a PDF with one rotated source page.

    The page rotation is stored in the source PDF so tests can verify
    export behavior when combined with per-page rotation metadata.
    """
    create_multi_page_pdf(file_path, page_count=2)
    document = fitz.open(file_path)
    try:
        document[1].set_rotation(90)
        document.save(file_path, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)
    finally:
        document.close()
    return file_path


def create_split_candidate_pdf(file_path: Path) -> Path:
    """Create a 7-page PDF useful for split-range and grouping scenarios."""
    return create_multi_page_pdf(file_path, page_count=7)
