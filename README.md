# pdf_viewer
An app to view and edit a pdf

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

Run the smoke test suite with:

```powershell
pytest
```

