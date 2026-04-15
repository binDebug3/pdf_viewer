# pdf_viewer
An app to view and edit a pdf

## Current UX Features

- Polished desktop layout with stronger hover and selection feedback in the toolbar, filmstrip, and inspector.
- Keyboard shortcuts for common actions like open, add, save-as, split mode, undo, and redo.
- Recent files list in the File menu for quick re-open.
- Last-session restore support on startup (toggleable from the File menu).
- Improved blank-state guidance to make first-run actions clear.

## Planning

See `docs/implementation-plan.md` for the phased implementation plan, architecture, MVP scope, and delivery milestones.

## Setup

Create the Conda environment from `environment.yml` and activate it:

```powershell
conda env create -f environment.yml
conda activate pdf-viewer
```

If you update the dependency list later, refresh the environment with:

```powershell
conda env update -f environment.yml --prune
```

## Run

Launch the app from the repository root:

```powershell
python -m app.main
```

## Test

Run all automated tests (unit, integration, and UI) with:

```powershell
pytest
```

Generate a coverage report with:

```powershell
pytest --cov=core --cov=services --cov-report=term-missing
```

