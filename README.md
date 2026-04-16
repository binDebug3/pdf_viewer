# PDF Viewer

PDF Viewer is a Windows desktop app for assembling and splitting PDF documents with a fast,
mouse-first workflow.

Use it when you need to:

- Open a PDF and inspect pages quickly.
- Add and join pages from multiple PDFs.
- Reorder pages with drag-and-drop.
- Rotate, duplicate, delete, and extract pages.
- Split one document into multiple outputs.
- Save your results with predictable export behavior.


## Quick Start (5 Minutes)

### 1. Create the environment

```powershell
conda env create -f environment.yml
conda activate pdf-viewer
```

Already created it before? Refresh dependencies:

```powershell
conda env update -f environment.yml --prune
```

### 2. Launch the app

From the repository root:

```powershell
python -m app.main
```

### 3. Do your first edit

1. Click **Open PDF**.
2. Add a second file with **Add/Join PDFs**.
3. Reorder pages in the bottom filmstrip.
4. Click **Save As** to export.


## Why This Project Exists

Many PDF tools are either too heavy, too web-centric, or too opaque for simple
document surgery. This project focuses on practical editing operations with responsive UI,
clear state, and undo/redo confidence.


## Feature Snapshot

- Desktop UI with strong hover/selection feedback across toolbar, filmstrip, and inspector.
- Keyboard shortcuts for common actions: open, add, save-as, split mode, undo, and redo.
- Recent files menu and last-session restore support.
- Split planning modes (including custom ranges) with output previews.
- Export flow with overwrite behavior support.
- Runtime logs and crash report generation for beta troubleshooting.


## Project Stack

- Python 3.12
- PySide6 (desktop UI)
- PyMuPDF (PDF load/render/export)
- PyInstaller (Windows packaging)
- Pytest + pytest-qt + pytest-cov (testing)


## Development Workflow

### Run tests

```powershell
pytest
```

The repository is configured to enforce minimum coverage on `core` and `services`.

### Run a focused test file

```powershell
pytest tests/unit/test_pdf_service.py
```

### Lint and format

```powershell
ruff check .
black .
```


## Packaging (Windows Beta)

Create the default one-folder build:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_windows.ps1
```

Create an optional one-file build:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_windows.ps1 -OneFile
```

See `docs/phase9-beta-readiness.md` for clean-machine verification, distribution guidance,
and runtime diagnostics expectations.


## Runtime Diagnostics

- Application logs: `%LOCALAPPDATA%/pdf_viewer/logs/app.log`
- Crash reports: `%LOCALAPPDATA%/pdf_viewer/crashes`

These are useful when reproducing beta issues or collecting user feedback.


## Repository Guide

- `app/`: app bootstrap and startup entrypoint.
- `core/`: domain models and session/history behavior.
- `services/`: rendering, export, settings, and runtime logging services.
- `ui/`: desktop UI panels, main window, dialogs, and interaction logic.
- `tests/`: unit, integration, and UI test coverage.
- `docs/`: implementation plan, QA matrix, and beta-readiness notes.


## Key Docs

- `docs/implementation-plan.md`: architecture, scope, and phased milestones.
- `docs/manual-qa-matrix.md`: manual validation scenarios.
- `docs/phase9-beta-readiness.md`: packaging and release gate checklist.


## Common Issues

### `ModuleNotFoundError` for `fitz` or `PySide6`

You are likely not running inside the `pdf-viewer` conda environment.

```powershell
conda activate pdf-viewer
python -m app.main
```

### Pytest fails because of coverage threshold in targeted test runs

If you only want quick local verification for a small subset of tests:

```powershell
pytest tests/unit/test_pdf_service.py --no-cov
```

Use full `pytest` before merging.


## Contributing Notes

- Keep behavior changes covered by tests in `tests/`.
- Prefer small, reviewable pull requests.
- Preserve user-facing workflow clarity (mouse-first, document-style interactions).


## License

This repository is licensed under the terms in `LICENSE`.

