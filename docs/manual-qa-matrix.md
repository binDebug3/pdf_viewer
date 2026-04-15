# Manual QA Matrix

## Scope

This matrix tracks behaviors that are hard to validate with deterministic automated checks,
including drag interactions and visual confidence cues.

## Environment

- OS: Windows 11 (baseline target)
- Python environment: conda env `pdf-viewer`
- Build: local source run via `python -m app.main`

## Workflow Matrix

| Feature Area | Scenario | Expected Result | Coverage |
| --- | --- | --- | --- |
| Startup | Launch app with no previous session | Main workspace shows blank-state guidance and primary actions | Automated + Manual |
| Startup | Launch app with valid last session and restore enabled | Last opened file loads and appears in viewer/filmstrip | Automated + Manual |
| Open | Open PDF via File menu | Thumbnails load, first page preview shown, inspector updates counts | Automated + Manual |
| Add/Join | Add second PDF to active session | Pages append in filmstrip with source boundaries and updated page count | Automated + Manual |
| Reorder | Drag a page left/right in filmstrip | Drop indicator is clear, page order changes, selection follows moved page | Manual |
| Multi-select | Ctrl-click / shift-like selection in filmstrip | Selected count updates and operations act on selected rows | Manual |
| Delete | Delete selected pages | Pages are removed, viewer/inspector update, empty-session placeholder when last page deleted | Automated + Manual |
| Duplicate | Duplicate selected pages | Duplicates are inserted after source pages and become selected | Automated + Manual |
| Split mode | Enter split mode and switch split source modes | Inspector controls become active and split preview updates live | Automated + Manual |
| Split custom ranges | Input valid and invalid custom ranges | Valid ranges show expected preview groups; invalid ranges show validation message | Automated + Manual |
| Split export | Save split documents | Output files match preview group count and page totals | Automated + Manual |
| Save As | Save edited session to new path | Exported PDF reflects page count/order and success status message | Automated + Manual |
| Overwrite prompt | Export to existing path with overwrite disabled | User receives overwrite confirmation prompt | Automated + Manual |
| Undo/Redo | Perform reorder/delete/duplicate then undo/redo | Session state transitions are consistent and toolbar state updates | Automated + Manual |
| Unsaved changes | Attempt to open another file after edits | Discard confirmation appears and blocks destructive change when canceled | Manual |
| Error handling | Open unreadable path or export with invalid extension | Error is surfaced and app remains usable | Automated + Manual |

## Sign-off

- Run through all manual-only rows before tagging a beta build.
- Capture regressions as test cases in `tests/integration` or `tests/ui` when feasible.
