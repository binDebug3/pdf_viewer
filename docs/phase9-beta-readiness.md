# Phase 9 Beta Readiness

## Packaging Strategy

- Packaging tool: PyInstaller.
- Default target: one-folder build for easier dependency verification.
- Optional target: one-file build via script switch.

Build command:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_windows.ps1
```

Build one-file variant:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_windows.ps1 -OneFile
```

## Distribution Guidance

- Zip distribution (recommended for beta): zip `dist/PDFViewer` and share the archive.
- Include this short run note for testers:
  - Extract archive.
  - Launch `PDFViewer.exe`.
  - Keep bundled files in the same extracted folder.

## Runtime Logging and Crash Reports

- Runtime logs:
  - Location: `%LOCALAPPDATA%/pdf_viewer/logs/app.log`.
  - Rotation: up to 5 files, approximately 1 MB each.
- Crash reports:
  - Location: `%LOCALAPPDATA%/pdf_viewer/crashes`.
  - Trigger: uncaught exceptions in main thread or background threads.
  - User feedback: a critical dialog is shown when possible.

## Clean Machine Verification Checklist

- Install no Python runtime and no developer tooling on test machine.
- Extract beta zip and launch `PDFViewer.exe`.
- Verify these workflows:
  - Open PDF.
  - Add PDF and reorder pages.
  - Split and export multiple files.
  - Save As with overwrite prompt path.
  - Undo and redo after edits.
- Validate logs are created in `%LOCALAPPDATA%/pdf_viewer/logs`.
- Force-test crash capture using a controlled exception build and confirm a crash report file appears.

## Release Gate

Beta is ready for external testing only when:

- PyInstaller build completes in CI or local release environment.
- Clean machine checklist passes.
- No critical crash without a generated report.
- Core manual QA matrix scenarios still pass.