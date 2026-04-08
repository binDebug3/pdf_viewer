# PDF Viewer Implementation Plan

## Product Direction

Build a Windows-only desktop app in Python for visual page-level PDF operations.

Primary workflows:
- Split PDFs into new documents using page selection and page ranges.
- Join multiple PDFs through direct page and file ordering.

Secondary workflows:
- Reorder pages.
- Rotate pages.
- Delete pages.
- Duplicate selected pages.

Non-goals for v1:
- Text editing inside PDF pages.
- Image editing inside PDF pages.
- OCR.
- Form authoring.
- Annotation and signature workflows.

## Recommended Stack

- UI framework: PySide6
- PDF rendering and manipulation: PyMuPDF
- Image utilities if needed: Pillow
- Packaging: PyInstaller
- Testing: pytest
- Optional UI assets: QtAwesome or SVG icons bundled locally

Why this stack:
- PySide6 gives a much better desktop experience than tkinter without forcing a web architecture.
- PyMuPDF is strong for page rendering, page extraction, document assembly, and export workflows.
- The stack is fast to build, local-first, and well suited to Windows packaging.

## UX Principles

- Make split and join visible at first glance.
- Prefer direct manipulation over modal-heavy workflows.
- Keep edits non-destructive until export.
- Default to Save As, with an optional overwrite setting.
- Optimize for mouse-first use, then add a small set of practical shortcuts.
- Keep the main workspace stable so users do not feel like they are entering separate tools.

## Main UI Shape

Main window layout:
- Top toolbar for primary actions.
- Left sidebar with page thumbnails and drag-and-drop ordering.
- Center canvas with large page preview.
- Right inspector panel for context-sensitive actions.
- Bottom status bar for page count, zoom, selection, and background task state.

Primary toolbar actions:
- Open PDF
- Add PDF
- Save As
- Split
- Join
- Rotate
- Delete
- Undo
- Redo

Split workflow:
- User selects one or more pages.
- Choose split by current page, selected pages, or page ranges.
- Preview the output grouping before export.
- Create one or more output PDFs from the selected groups.

Join workflow:
- User opens one PDF or starts empty.
- Drag additional PDFs into the thumbnail list.
- Insert at drop position.
- Reorder pages visually before export.

## Architecture Overview

Use a layered structure so the UI remains simple and editing logic stays testable.

Suggested structure:

```text
pdf_viewer/
  app/
    main.py
    bootstrap.py
  ui/
    main_window.py
    toolbar.py
    thumbnail_panel.py
    viewer_panel.py
    inspector_panel.py
    dialogs/
      export_dialog.py
      settings_dialog.py
  core/
    models/
      document_session.py
      page_item.py
      split_spec.py
    commands/
      base_command.py
      split_document.py
      insert_document.py
      reorder_pages.py
      rotate_pages.py
      delete_pages.py
      extract_pages.py
    state/
      app_state.py
      selection_state.py
      history.py
  services/
    pdf_service.py
    render_service.py
    export_service.py
    settings_service.py
    worker_service.py
  adapters/
    pymupdf_adapter.py
  assets/
    icons/
  tests/
    unit/
    integration/
```

Core responsibilities:
- `ui`: widgets, event wiring, visual state.
- `core.models`: app-facing document structures independent of the UI toolkit.
- `core.commands`: undoable user actions.
- `core.state`: active tool, selection, history, session flags.
- `services`: file I/O, render caching, export, settings persistence, background jobs.
- `adapters`: thin wrapper around PyMuPDF so backend details do not leak into the app.

## Data Model Strategy

Represent the working document as a session rather than editing files directly.

Suggested model concepts:
- `DocumentSession`: the in-memory workspace made from one or more source PDFs.
- `PageItem`: a page reference with source file, source page index, rotation, and transient preview metadata.
- `SplitSpec`: selected pages or page ranges grouped into one or more output documents.
- `CommandHistory`: undo and redo stack.

Important rule:
- Structural edits update the session model immediately.
- Final PDF bytes are generated only when exporting or explicitly saving.

This keeps the app responsive and reduces the risk of corrupting source files.

## Settings Strategy

Store simple local settings such as:
- Last opened directory.
- Last export directory.
- Overwrite enabled or disabled.
- Thumbnail size.
- Default zoom behavior.
- Whether to restore the last session.

Use a small JSON config or `QSettings`.

## Phased Delivery Plan

### Phase 0: Project Setup

Goal:
- Create a clean desktop application skeleton with the chosen stack and developer workflow.

Tasks:
- Initialize Python project structure.
- Add dependency management.
- Add a runnable app entry point.
- Set up formatting, linting, and test tooling.
- Add a basic main window using PySide6.
- Add repo documentation for setup and running locally.

Deliverables:
- App launches to a blank main window.
- Dependencies install cleanly on Windows.
- Tests run successfully.

Acceptance criteria:
- `python -m app.main` launches the application.
- A first-time contributor can set up the project from the README.

### Phase 1: Shell UI and Navigation

Goal:
- Build the main document-style interface without full PDF editing logic yet.

Tasks:
- Create the top toolbar.
- Create the thumbnail sidebar.
- Create the viewer canvas area.
- Create the right-side inspector panel.
- Add drag-and-drop target areas.
- Add empty states for no file loaded.
- Add basic status bar feedback.

UX requirements:
- Empty state explains the two main actions: open a PDF and add PDFs to join.
- The initial layout immediately suggests how the app is used.

Deliverables:
- Clickable UI scaffold.
- Responsive resizing.
- Placeholder interactions for split/join actions.

Acceptance criteria:
- The app feels like a document workspace, not a utility dialog.
- A user can identify the main workflow within a few seconds.

### Phase 2: PDF Loading and Rendering

Goal:
- Load PDFs and display pages reliably.

Tasks:
- Implement file open and drag-and-drop import.
- Load a PDF into a `DocumentSession`.
- Render thumbnail previews.
- Render the selected page in the main viewer.
- Implement zoom and fit-to-window behavior.
- Add caching for rendered previews.
- Show loading state for large documents.

Technical notes:
- Render thumbnails at lower resolution than the main preview.
- Cache preview bitmaps by page id, zoom bucket, and rotation state.
- Use background workers for heavy rendering.

Deliverables:
- Users can open and browse a PDF.
- The thumbnail list and main preview stay in sync.

Acceptance criteria:
- PDFs with moderate page counts feel responsive.
- Selecting a thumbnail updates the main preview without visible lag in common cases.

### Phase 3: Join and Page Assembly

Goal:
- Make multi-document composition a first-class workflow.

Tasks:
- Add support for importing multiple PDFs into one session.
- Allow insert-at-position from drag-and-drop.
- Allow drag-reorder across all pages in the session.
- Show file boundaries subtly in the thumbnail list if useful.
- Support delete, duplicate, and extract for selected pages.
- Add multi-select interaction optimized for mouse use.

UX requirements:
- Adding a second PDF should feel like extending the current document, not opening a different mode.
- Reordering should provide clear drop indicators.

Deliverables:
- Users can join PDFs and rearrange pages visually.

Acceptance criteria:
- A user can combine two PDFs and export the result without confusion.
- Reordering is stable and undoable.

### Phase 4: Split Workflow

Goal:
- Implement the core split experience with high usability.

Tasks:
- Add split mode for selected pages and page ranges.
- Add inspector controls for current page, selected pages, custom ranges, odd pages, and even pages.
- Show a live preview of which pages will go into each output document.
- Add actions to create one output file or multiple output files from a split plan.
- Allow reset and edit of the current split plan before export.
- Ensure selection, preview, and export plan stay in sync.

UX requirements:
- The split tool must make it obvious which pages are included in each output.
- Common range patterns should be easy to apply without typing when possible.
- Exiting split mode without applying should be predictable.

Deliverables:
- Fully usable split workflow.

Acceptance criteria:
- A user can split a document by page selection or page range without reading documentation.
- Creating multiple output PDFs from a split plan takes only a few clicks.

### Phase 5: Undo/Redo and Session Reliability

Goal:
- Make all editing operations safe and reversible.

Tasks:
- Introduce a command pattern for all page operations.
- Add undo/redo stacks.
- Track dirty state.
- Warn before closing unsaved sessions.
- Add recovery-friendly session behavior where practical.

Operations that should be undoable:
- Insert document
- Reorder pages
- Create or modify split plans where they affect session state
- Rotate pages
- Delete pages
- Duplicate pages
- Extract selection state changes where appropriate

Deliverables:
- Robust editing history.

Acceptance criteria:
- All user-visible edits can be reversed reliably.
- The app does not silently discard meaningful work.

### Phase 6: Export, Save As, and Overwrite Option

Goal:
- Convert the session into a new PDF safely and clearly.

Tasks:
- Implement `Save As` as the default export path.
- Add overwrite option in settings and export flow.
- Validate file paths and overwrite prompts.
- Preserve page order, rotation, split selection, and deletions in output.
- Add export progress and error handling.

UX requirements:
- Default behavior must protect original files.
- Overwrite should be available, but never ambiguous.

Deliverables:
- Reliable PDF export.

Acceptance criteria:
- Exported files reflect the exact session state.
- The user always knows whether they are creating a new file or overwriting an existing one.

### Phase 7: Polish and Usability Pass

Goal:
- Make the app feel deliberate and pleasant rather than merely functional.

Tasks:
- Refine spacing, typography, icon consistency, and panel proportions.
- Improve hover states, selection visuals, and drop indicators.
- Add keyboard shortcuts for common actions without making the UI keyboard-centric.
- Add recent files.
- Add last-session restore if stable enough.
- Improve empty states and inline guidance.

Polish targets:
- Modern neutral color palette.
- Clean iconography.
- Good default window sizing.
- Fast visible feedback for user actions.

Deliverables:
- A coherent and visually polished desktop experience.

Acceptance criteria:
- First-time users can discover the main flows with minimal friction.
- The app no longer feels like a prototype.

### Phase 8: Test Implementation and Test Review

Goal:
- Build a thorough automated and manual test suite that covers all user-visible functionality and validates that the app behaves consistently across editing, preview, and export flows.

Tasks:
- Write unit tests for core models, command objects, and service logic.
- Write integration tests for document loading, rendering, selection, page operations, undo/redo, and export.
- Add fixture PDFs that cover single-page, multi-page, mixed-size, rotated, and pre-split-worthy page patterns.
- Add regression tests for previously fixed bugs and edge cases.
- Add UI-level tests for key mouse-first interactions where practical.
- Review the test suite for missing feature coverage, weak assertions, and overly brittle tests.
- Verify that preview state and exported output remain aligned for split selection, rotation, ordering, deletion, duplication, and extraction.
- Add test coverage reporting and a minimum coverage target for core modules.
- Create and maintain a manual QA matrix for behaviors that are difficult to automate fully.

Coverage requirements:
- Application startup and blank-state behavior.
- Open PDF from file picker.
- Drag-and-drop PDF import.
- Thumbnail rendering and selection sync.
- Main page preview rendering.
- Zoom and fit-to-window behavior.
- Multi-document join flow.
- Insert-at-position behavior.
- Drag-reorder within and across imported documents.
- Multi-select behavior for page operations.
- Split mode entry and exit.
- Split plan editing for current page, selected pages, and custom page ranges.
- Split preview updates in the inspector and output summary.
- Reset split plan behavior.
- Rotate page behavior.
- Delete page behavior.
- Duplicate page behavior.
- Extract selected pages behavior.
- Undo and redo for every supported page operation.
- Dirty-state tracking.
- Close-with-unsaved-changes warnings.
- Save As export.
- Optional overwrite flow.
- Export correctness for page order, split ranges, rotation, and page count.
- Recent files and last-session restore if included in scope.
- Error handling for unreadable files, invalid paths, and export failures.
- Responsiveness expectations for larger documents.

Test suite structure:
- `tests/unit` for model, command, state, and service logic.
- `tests/integration` for session, rendering, export, and multi-step workflows.
- `tests/ui` for critical widget and interaction tests.
- `tests/fixtures` for sample PDFs and expected-output artifacts.

Review checklist:
- Every feature in the MVP has at least one happy-path test.
- Every destructive or stateful operation has negative-path or edge-case coverage.
- Every undoable command is validated for both do and undo behavior.
- Export tests verify actual output properties, not just that a file was created.
- UI tests focus on stable behavior rather than fragile pixel-perfect assertions.
- Manual QA covers workflows that rely heavily on drag interaction and visual confidence.

Deliverables:
- A complete test suite that runs locally and in CI.
- A documented manual QA checklist mapped to features.
- Coverage reports for core modules and critical workflows.

Acceptance criteria:
- All MVP functionality is explicitly covered by automated tests, manual QA, or both.
- Regressions in split, join, reorder, undo/redo, and export are likely to be caught before release.
- The test suite is reviewed for completeness and gaps are documented or fixed.

### Phase 9: Packaging and Beta Readiness

Goal:
- Produce a distributable Windows build and stabilize the release path.

Tasks:
- Package with PyInstaller.
- Verify assets and dependencies are bundled correctly.
- Test on a clean Windows machine.
- Add installer or zip-based distribution instructions.
- Finalize error logging and crash reporting strategy.

Deliverables:
- A Windows build suitable for testing by others.

Acceptance criteria:
- The packaged app launches and performs the core workflows on a machine without a development environment.

## Suggested Execution Order

Build in this order:
1. Phase 0
2. Phase 1
3. Phase 2
4. Phase 3
5. Phase 4
6. Phase 5
7. Phase 6
8. Phase 7
9. Phase 8
10. Phase 9

This order is deliberate:
- Join requires strong session and page-list behavior, so it comes before split polish.
- Split is a flagship feature, but it depends on stable rendering, selection, and export planning.
- Undo/redo should land before export is treated as complete.
- A dedicated test phase before packaging reduces the risk of shipping a polished but unreliable beta build.

## MVP Definition

The app is MVP-complete when it can do all of the following well:
- Open a PDF.
- Add additional PDFs into the same session.
- Show thumbnails and a main preview.
- Reorder pages visually.
- Split one or many page selections or ranges into output PDFs.
- Rotate and delete pages.
- Export using Save As.
- Undo and redo all edits.

Anything beyond that is post-MVP.

## Risks and Mitigations

### Risk: UI lag on large PDFs

Mitigation:
- Use background workers.
- Cache thumbnails and page previews.
- Limit rerendering to changed pages.

### Risk: Split behavior feels unclear

Mitigation:
- Show a persistent split inspector.
- Make scope explicit: current page, selected pages, custom ranges, and output grouping.
- Add obvious apply, preview, and reset actions.

### Risk: Merge and reorder logic becomes fragile

Mitigation:
- Keep `PageItem` immutable where practical.
- Route edits through command objects.
- Add targeted integration tests around page ordering.

### Risk: Export output differs from preview

Mitigation:
- Derive preview and export from the same split selection and rotation metadata.
- Test round-trip output against expected page counts and bounds.

## Test Strategy

Testing is a formal delivery phase, not just a side activity during implementation.

Unit tests:
- Session creation and page identity rules.
- Page insertion, deletion, duplication, extraction, rotation, and ordering.
- Split plan creation, validation, and reset behavior.
- Undo and redo behavior for every command.
- Dirty-state tracking and command history rules.
- Export planning logic and overwrite decision logic.
- Settings persistence for recent files and overwrite preferences.

Integration tests:
- Open sample PDF and render first page.
- Import second PDF and join pages.
- Reorder pages across combined documents.
- Split selected pages or ranges and export.
- Rotate, delete, duplicate, and extract pages before export.
- Verify preview state matches exported output metadata.
- Save As and overwrite behavior.
- Close with unsaved changes.
- Failure handling for unreadable PDFs and export errors.

Manual QA checklist:
- First-run blank state clarity.
- Drag-and-drop import.
- Multi-select pages with mouse interactions.
- Split selection and custom range editing.
- Join and reorder across multiple imported files.
- Undo and redo after mixed operations.
- Export after mixed operations.
- Close with unsaved changes.
- Large document responsiveness.

## First Sprint Recommendation

If you want the fastest path to visible progress, the first sprint should cover:
- Phase 0 complete.
- Phase 1 complete.
- Enough of Phase 2 to open a PDF, show thumbnails, and preview the selected page.

That gives a usable vertical slice and validates the desktop stack before deeper editing work.

## Second Sprint Recommendation

After the first slice is stable, build:
- Core of Phase 3 for join and reorder.
- Core of Phase 4 for split mode and apply-to-selection.

That gets the app to the main user value quickly.

## Definition of Done for v1

Version 1 is done when:
- Split and join feel like the natural center of the app.
- Common page operations are stable and undoable.
- Save As is reliable.
- The UI looks intentional and modern.
- A packaged Windows build can be handed to another user without setup friction.