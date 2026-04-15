from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from PySide6.QtGui import QAction
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QProgressDialog,
    QVBoxLayout,
    QWidget,
)

from core.models.document_session import DocumentSession
from core.models.split_spec import SplitSpec
from core.state.history import HistoryStep, SessionHistory
from services.export_service import ExportService
from services.pdf_service import PdfService
from services.settings_service import SettingsService

from ui.inspector_panel import InspectorPanel
from ui.thumbnail_panel import ThumbnailPanel
from ui.toolbar import AppToolBar
from ui.viewer_panel import ViewerPanel


class MainWindow(QMainWindow):
    STARTUP_HINT = "Open a PDF or drop one in the filmstrip to start editing."

    def __init__(self) -> None:
        super().__init__()
        self._pdf_service = PdfService()
        self._export_service = ExportService(self._pdf_service)
        self._settings_service = SettingsService()
        self._session: DocumentSession | None = None
        self._selected_page_indexes: list[int] = []
        self._history = SessionHistory()
        self._split_mode_active = False
        self._split_spec = SplitSpec(mode="current")
        self._recent_file_actions: list[QAction] = []
        self.setWindowTitle("PDF Viewer")
        self.resize(1180, 760)
        self.setMinimumSize(860, 560)
        self.statusBar().showMessage(self.STARTUP_HINT)
        self._build_ui()
        self._build_menu()
        self._build_toolbar()
        self._refresh_recent_files_menu()

    def _build_menu(self) -> None:
        file_menu = self.menuBar().addMenu("&File")

        open_action = file_menu.addAction("Open PDF...")
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(lambda: self._handle_toolbar_action("open"))

        add_action = file_menu.addAction("Add PDF...")
        add_action.setShortcut("Ctrl+Shift+O")
        add_action.triggered.connect(lambda: self._handle_toolbar_action("add"))

        save_as_action = file_menu.addAction("Save As...")
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(lambda: self._handle_toolbar_action("save_as"))

        file_menu.addSeparator()
        recent_header = file_menu.addAction("Recent Files")
        recent_header.setEnabled(False)

        for _index in range(SettingsService.MAX_RECENT_FILES):
            action = file_menu.addAction("")
            action.setVisible(False)
            action.triggered.connect(
                lambda _checked=False, value=action: self._open_recent_file(str(value.data()))
            )
            self._recent_file_actions.append(action)

        file_menu.addSeparator()
        restore_last_action = file_menu.addAction("Restore Last Session")
        restore_last_action.triggered.connect(self._attempt_restore_last_session)

    def _build_toolbar(self) -> None:
        self._toolbar = AppToolBar(self._handle_toolbar_action, self)
        self.addToolBar(self._toolbar)
        self._toolbar.set_history_state(can_undo=False, can_redo=False)

    def _build_ui(self) -> None:
        root = QWidget(self)
        self.setCentralWidget(root)

        outer = QVBoxLayout(root)
        outer.setContentsMargins(8, 8, 8, 8)
        outer.setSpacing(4)

        workspace = self._build_workspace_panel()
        page_strip = self._build_page_strip_panel()

        outer.addWidget(workspace, stretch=1)
        outer.addWidget(page_strip)

    def _build_workspace_panel(self) -> QWidget:
        container = QWidget(self)
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self._viewer_panel = ViewerPanel(self)
        self._inspector_panel = InspectorPanel(self)
        self._inspector_panel.split_options_changed.connect(self._update_split_plan)
        self._inspector_panel.split_reset_requested.connect(self._reset_split_plan)

        layout.addWidget(self._viewer_panel, stretch=1)
        layout.addWidget(self._inspector_panel)
        return container

    def _build_page_strip_panel(self) -> QWidget:
        self._thumbnail_panel = ThumbnailPanel(self)
        self._thumbnail_panel.page_selected.connect(self._select_page)
        self._thumbnail_panel.page_clicked.connect(self._handle_page_clicked)
        self._thumbnail_panel.selection_changed.connect(self._handle_selection_changed)
        self._thumbnail_panel.page_reordered.connect(self._reorder_page)
        return self._thumbnail_panel

    def _handle_toolbar_action(self, action_id: str) -> None:
        if self._split_mode_active and action_id not in {"save_splits", "cancel_split", "split"}:
            self.statusBar().showMessage(
                "Save or cancel split mode before using other actions.",
                3000,
            )
            return

        if action_id == "open":
            self._open_pdf()
            return
        if action_id == "add":
            self._add_pdf()
            return
        if action_id == "save_as":
            self._save_as()
            return
        if action_id == "delete":
            self._delete_selected_pages()
            return
        if action_id == "duplicate":
            self._duplicate_selected_pages()
            return
        if action_id == "split":
            self._enter_split_mode()
            return
        if action_id == "save_splits":
            self._save_split_documents()
            return
        if action_id == "cancel_split":
            self._exit_split_mode(clear_markers=True)
            return
        if action_id == "join":
            self._join_pdfs()
            return
        if action_id == "rotate":
            self._rotate_selected_pages()
            return
        if action_id == "undo":
            self._undo()
            return
        if action_id == "redo":
            self._redo()
            return

        self.statusBar().showMessage("Action not implemented yet.", 4000)

    def _open_pdf(self) -> None:
        if not self._confirm_discard_unsaved_changes():
            return

        file_path, _selected_filter = QFileDialog.getOpenFileName(
            self,
            "Open PDF",
            "",
            "PDF Files (*.pdf)",
        )
        if not file_path:
            return

        session = self._pdf_service.load_document(file_path)
        self._load_session(session)
        self._remember_opened_file(file_path)
        self.statusBar().showMessage(
            f"Loaded {session.page_count} pages from {session.source_path.name}",
            5000,
        )

    def _add_pdf(self) -> None:
        file_path, _selected_filter = QFileDialog.getOpenFileName(
            self,
            "Add PDF",
            "",
            "PDF Files (*.pdf)",
        )
        if not file_path:
            return

        if self._session is not None and self._history.is_dirty:
            if not self._confirm_discard_unsaved_changes():
                return

        if self._session is None:
            self._load_session(self._pdf_service.load_document(file_path))
            self._remember_opened_file(file_path)
            self.statusBar().showMessage(
                (
                    f"Loaded {self._session.page_count if self._session else 0} pages "
                    f"from {Path(file_path).name}"
                ),
                5000,
            )
            return

        before = self._session.clone()
        page_count = self._pdf_service.get_page_count(file_path)
        self._session.append_document(file_path, page_count)
        self._remember_opened_file(file_path)
        self._record_history_change(before, "Add PDF")
        self._refresh_thumbnails(preserve_selection=True)
        self.statusBar().showMessage(
            f"Added {page_count} pages from {Path(file_path).name}",
            5000,
        )

    def _join_pdfs(self) -> None:
        file_paths, _selected_filter = QFileDialog.getOpenFileNames(
            self,
            "Join PDFs",
            "",
            "PDF Files (*.pdf)",
        )
        if not file_paths:
            return

        if self._session is None:
            primary_path = file_paths[0]
            session = self._pdf_service.load_document(primary_path)
            self._load_session(session)
            self._remember_opened_file(primary_path)
            join_paths = file_paths[1:]
        else:
            join_paths = file_paths

        if self._session is None:
            return

        before = self._session.clone()
        total_added_pages = 0
        first_added_index = self._session.page_count

        for file_path in join_paths:
            page_count = self._pdf_service.get_page_count(file_path)
            if page_count <= 0:
                continue
            self._session.append_document(file_path, page_count)
            self._remember_opened_file(file_path)
            total_added_pages += page_count

        if total_added_pages == 0:
            self.statusBar().showMessage("No additional pages were added during join.", 3000)
            return

        self._record_history_change(before, "Join PDFs")
        self._selected_page_indexes = [first_added_index]
        self._refresh_thumbnails(preserve_selection=True)
        self._thumbnail_panel.set_current_page(first_added_index)
        self._select_page(first_added_index)
        self.statusBar().showMessage(
            f"Joined {len(join_paths)} file(s), adding {total_added_pages} page(s).",
            5000,
        )

    def _rotate_selected_pages(self) -> None:
        if self._session is None or not self._session.pages:
            self.statusBar().showMessage("Open a PDF before rotating pages.", 3000)
            return

        target_indexes = self._selected_page_indexes or [self._session.selected_page_index]
        before = self._session.clone()
        rotated_indexes = self._session.rotate_pages(target_indexes, degrees=90)
        if not rotated_indexes:
            self.statusBar().showMessage("Select at least one page to rotate.", 3000)
            return

        self._record_history_change(before, "Rotate pages")
        self._selected_page_indexes = rotated_indexes
        self._refresh_thumbnails(preserve_selection=True)
        self._thumbnail_panel.set_current_page(rotated_indexes[0])
        self._select_page(rotated_indexes[0])
        self.statusBar().showMessage(
            f"Rotated {len(rotated_indexes)} page(s) clockwise.",
            3000,
        )

    def _remember_opened_file(self, file_path: str | Path) -> None:
        self._settings_service.add_recent_file(file_path)
        self._settings_service.set_last_session_path(file_path)
        self._refresh_recent_files_menu()

    def _refresh_recent_files_menu(self) -> None:
        recent_paths = self._settings_service.recent_files()
        for index, action in enumerate(self._recent_file_actions):
            if index < len(recent_paths):
                recent_path = recent_paths[index]
                action.setText(f"{index + 1}. {Path(recent_path).name}")
                action.setToolTip(recent_path)
                action.setData(recent_path)
                action.setVisible(True)
                continue

            action.setVisible(False)
            action.setData(None)

    def _open_recent_file(self, file_path: str) -> None:
        if not file_path:
            return
        if not Path(file_path).exists():
            self._settings_service.remove_recent_file(file_path)
            self._refresh_recent_files_menu()
            self.statusBar().showMessage("Recent file no longer exists.", 3000)
            return
        if not self._confirm_discard_unsaved_changes():
            return

        try:
            session = self._pdf_service.load_document(file_path)
        except (OSError, ValueError) as error:
            self._settings_service.remove_recent_file(file_path)
            self._refresh_recent_files_menu()
            self.statusBar().showMessage(f"Unable to open recent file: {error}", 5000)
            return

        self._load_session(session)
        self._remember_opened_file(file_path)
        self.statusBar().showMessage(
            f"Restored {session.page_count} pages from {session.source_path.name}",
            5000,
        )

    def _attempt_restore_last_session(self) -> None:
        if self._session is not None:
            return
        if not self._settings_service.should_restore_last_session():
            return

        file_path = self._settings_service.last_session_path()
        if file_path is None:
            return

        try:
            session = self._pdf_service.load_document(file_path)
        except (OSError, ValueError):
            self._settings_service.clear_last_session_path()
            return

        self._load_session(session)
        self._remember_opened_file(file_path)
        self.statusBar().showMessage(
            f"Restored last session: {session.source_path.name}",
            5000,
        )

    def _load_session(self, session: DocumentSession) -> None:
        self._exit_split_mode(clear_markers=True)
        self._session = session
        self._history.reset(session)
        self._refresh_thumbnails(preserve_selection=False)
        self._select_page(0)
        self._refresh_history_ui()

    def _refresh_thumbnails(self, preserve_selection: bool) -> None:
        if self._session is None:
            self._thumbnail_panel.clear_pages()
            return

        document_breaks = {
            index
            for index, page in enumerate(self._session.pages)
            if index > 0 and page.source_path != self._session.pages[index - 1].source_path
        }
        thumbnails = [
            self._pdf_service.render_thumbnail(page.source_path, page.source_page_index)
            for page in self._session.pages
        ]
        self._thumbnail_panel.set_pages(thumbnails, document_breaks)
        self._apply_split_markers()
        if preserve_selection and self._session.pages:
            self._thumbnail_panel.set_current_page(self._session.selected_page_index)
            self._thumbnail_panel.set_selected_pages(self._selected_page_indexes)

    def _reorder_page(self, source_index: int, destination_index: int) -> None:
        if self._session is None:
            return

        before = self._session.clone()
        selected_index = self._session.move_page(source_index, destination_index)
        self._record_history_change(before, "Reorder pages")
        self._selected_page_indexes = [selected_index]
        self._refresh_thumbnails(preserve_selection=True)
        self._thumbnail_panel.set_current_page(selected_index)
        self._select_page(selected_index)
        self.statusBar().showMessage(
            f"Moved page {source_index + 1} to position {destination_index + 1}",
            3000,
        )

    def _delete_selected_pages(self) -> None:
        if self._session is None or not self._selected_page_indexes:
            self.statusBar().showMessage("Select at least one page to delete.", 3000)
            return

        before = self._session.clone()
        selected_index = self._session.delete_pages(self._selected_page_indexes)
        self._record_history_change(before, "Delete pages")
        deleted_count = len(self._selected_page_indexes)
        self._selected_page_indexes = [] if selected_index is None else [selected_index]
        self._refresh_thumbnails(preserve_selection=True)

        if selected_index is None:
            self._viewer_panel.show_placeholder(
                "No pages left. Open a PDF or add another file to continue."
            )
            self._inspector_panel.set_blank_state()
        else:
            self._thumbnail_panel.set_current_page(selected_index)
            self._select_page(selected_index)

        self.statusBar().showMessage(f"Deleted {deleted_count} page(s)", 3000)

    def _duplicate_selected_pages(self) -> None:
        if self._session is None or not self._selected_page_indexes:
            self.statusBar().showMessage("Select at least one page to duplicate.", 3000)
            return

        before = self._session.clone()
        inserted_indexes = self._session.duplicate_pages(self._selected_page_indexes)
        if not inserted_indexes:
            return

        self._record_history_change(before, "Duplicate pages")
        self._selected_page_indexes = inserted_indexes
        self._refresh_thumbnails(preserve_selection=True)
        self._thumbnail_panel.set_current_page(inserted_indexes[0])
        self._select_page(inserted_indexes[0])
        self.statusBar().showMessage(f"Duplicated {len(inserted_indexes)} page(s)", 3000)

    def _split_pdf(self) -> None:
        self._enter_split_mode()

    def _enter_split_mode(self) -> None:
        if self._session is None or not self._session.pages:
            self.statusBar().showMessage("Open a PDF before splitting pages.", 3000)
            return

        if self._split_mode_active:
            self.statusBar().showMessage(
                "Split mode is already active. Click pages to add or remove breaks.",
                3000,
            )
            return

        self._split_mode_active = True
        self._split_spec = SplitSpec(mode="selected")
        self._selected_page_indexes = []
        self._thumbnail_panel.set_selected_pages([])
        self._toolbar.set_split_mode(True)
        self._inspector_panel.set_split_controls(
            self._split_spec.mode,
            self._split_spec.custom_ranges,
            self._split_spec.create_multiple_files,
        )
        self._apply_split_markers()
        self._update_inspector()
        self.statusBar().showMessage(
            "Split mode active. Choose a split source and review the live preview.",
            5000,
        )

    def _save_split_documents(self) -> None:
        if self._session is None or not self._session.pages:
            return

        error = self._split_spec.validation_error(
            page_count=self._session.page_count,
            current_page_index=self._session.selected_page_index,
            selected_indexes=self._selected_page_indexes,
        )
        if error is not None:
            self.statusBar().showMessage(error, 3000)
            return

        groups = self._split_spec.build_output_groups(
            page_count=self._session.page_count,
            current_page_index=self._session.selected_page_index,
            selected_indexes=self._selected_page_indexes,
        )
        if not groups:
            self.statusBar().showMessage("No split groups are available to export.", 3000)
            return

        output_path, _selected_filter = QFileDialog.getSaveFileName(
            self,
            "Save split PDFs",
            str(self._session.source_path),
            "PDF Files (*.pdf)",
        )
        if not output_path:
            return

        destination = self._normalize_pdf_output_path(output_path)
        allow_overwrite = self._settings_service.overwrite_existing

        def export_split_groups() -> list[Path]:
            return self._export_service.export_groups(
                self._session,
                groups,
                base_output_path=destination,
                allow_overwrite=allow_overwrite,
            )

        try:
            exported_paths = self._run_export_task(
                "Exporting split documents...",
                export_split_groups,
            )
        except FileExistsError as error:
            if not self._confirm_overwrite(str(error)):
                self.statusBar().showMessage("Split export canceled.", 3000)
                return

            exported_paths = self._run_export_task(
                "Exporting split documents...",
                lambda: self._export_service.export_groups(
                    self._session,
                    groups,
                    base_output_path=destination,
                    allow_overwrite=True,
                ),
            )
        except (OSError, ValueError) as error:
            self._show_export_error("Split export failed", str(error))
            return

        self._settings_service.set_last_export_directory(destination.parent)
        self._exit_split_mode(clear_markers=True)
        self.statusBar().showMessage(
            f"Created {len(exported_paths)} split PDF(s) starting at {exported_paths[0].name}",
            5000,
        )

    def _save_as(self) -> None:
        if self._session is None or not self._session.pages:
            self.statusBar().showMessage("Open a PDF before using Save As.", 3000)
            return

        default_path = self._default_export_path()
        output_path, _selected_filter = QFileDialog.getSaveFileName(
            self,
            "Save As",
            str(default_path),
            "PDF Files (*.pdf)",
        )
        if not output_path:
            return

        destination = self._normalize_pdf_output_path(output_path)
        allow_overwrite = self._settings_service.overwrite_existing

        try:
            exported_path = self._run_export_task(
                "Exporting PDF...",
                lambda: self._export_service.export_session(
                    self._session,
                    destination,
                    allow_overwrite=allow_overwrite,
                ),
            )
        except FileExistsError as error:
            if not self._confirm_overwrite(str(error)):
                self.statusBar().showMessage("Save As canceled.", 3000)
                return

            exported_path = self._run_export_task(
                "Exporting PDF...",
                lambda: self._export_service.export_session(
                    self._session,
                    destination,
                    allow_overwrite=True,
                ),
            )
        except (OSError, ValueError) as error:
            self._show_export_error("Save As failed", str(error))
            return

        self._settings_service.set_last_export_directory(exported_path.parent)
        self._history.mark_clean()
        self._refresh_history_ui()
        self.statusBar().showMessage(f"Saved session as {exported_path.name}", 5000)

    def _exit_split_mode(self, clear_markers: bool) -> None:
        self._split_mode_active = False
        if clear_markers:
            self._split_spec = SplitSpec(mode="current")
        if hasattr(self, "_toolbar"):
            self._toolbar.set_split_mode(False)
        self._apply_split_markers()
        self._update_inspector()

    def _handle_page_clicked(self, page_index: int) -> None:
        if self._session is None or not self._session.pages:
            return

        if self._split_mode_active:
            toggled_indexes = set(self._selected_page_indexes)
            if page_index in toggled_indexes:
                toggled_indexes.remove(page_index)
            else:
                toggled_indexes.add(page_index)

            self._selected_page_indexes = sorted(toggled_indexes)
            self._thumbnail_panel.set_selected_pages(self._selected_page_indexes)
            self._thumbnail_panel.set_current_page(page_index)
            self._select_page(page_index)
            self._apply_split_markers()
            self._update_inspector()
            self.statusBar().showMessage(
                f"Split selection: {len(self._selected_page_indexes)} page(s)",
                2000,
            )
            return

        self._select_page(page_index)

    def _apply_split_markers(self) -> None:
        if not hasattr(self, "_thumbnail_panel"):
            return
        split_starts = set()
        if self._split_mode_active and self._session is not None:
            try:
                groups = self._split_spec.build_output_groups(
                    page_count=self._session.page_count,
                    current_page_index=self._session.selected_page_index,
                    selected_indexes=self._selected_page_indexes,
                )
                split_starts = {group[0] for group in groups if group}
            except ValueError:
                split_starts = set()
        self._thumbnail_panel.set_split_starts(split_starts)

    def _select_page(self, page_index: int) -> None:
        if self._session is None or not self._session.pages:
            return

        self._session.select_page(page_index)
        page = self._session.selected_page
        if page is None:
            return

        pixmap = self._pdf_service.render_page(
            page.source_path,
            page.source_page_index,
            max_width=self._viewer_panel.render_target_width(),
        )
        self._viewer_panel.show_page(pixmap, page_index, self._session.page_count)
        self._thumbnail_panel.set_current_page(page_index)
        self._update_inspector()

    def _handle_selection_changed(self, indexes: list[int]) -> None:
        self._selected_page_indexes = indexes
        if not indexes:
            self._update_inspector()
            return

        if self._session is not None:
            self._update_inspector()

    def _update_inspector(self) -> None:
        if self._session is None or not self._session.pages:
            self._inspector_panel.set_blank_state()
            return

        split_preview_lines: list[str] = []
        if self._split_mode_active:
            split_preview_lines = self._split_spec.describe_output_groups(
                page_count=self._session.page_count,
                current_page_index=self._session.selected_page_index,
                selected_indexes=self._selected_page_indexes,
            )

            validation_error = self._split_spec.validation_error(
                page_count=self._session.page_count,
                current_page_index=self._session.selected_page_index,
                selected_indexes=self._selected_page_indexes,
            )
            preview_text = (
                validation_error
                if validation_error is not None
                else "\n".join(split_preview_lines) or "No split output yet."
            )
            self._inspector_panel.set_split_preview(preview_text)
            self._inspector_panel.set_split_controls(
                self._split_spec.mode,
                self._split_spec.custom_ranges,
                self._split_spec.create_multiple_files,
            )
        else:
            self._inspector_panel.set_split_preview(
                "Preview will appear when split mode is active."
            )

        self._inspector_panel.set_document_state(
            str(self._session.source_path),
            self._session.page_count,
            self._session.selected_page_index,
            self._session.source_count,
            max(1, len(self._selected_page_indexes)),
            split_mode_active=self._split_mode_active,
            split_start_indexes=[],
            split_preview_lines=split_preview_lines,
        )

    def _update_split_plan(
        self,
        mode: str,
        custom_ranges: str,
        create_multiple_files: bool,
    ) -> None:
        if not self._split_mode_active:
            return
        self._split_spec = SplitSpec(
            mode=mode,
            custom_ranges=custom_ranges,
            create_multiple_files=create_multiple_files,
        )
        self._apply_split_markers()
        self._update_inspector()

    def _reset_split_plan(self) -> None:
        if not self._split_mode_active:
            return
        self._split_spec = SplitSpec(mode="selected")
        self._apply_split_markers()
        self._update_inspector()
        self.statusBar().showMessage("Split plan reset.", 2500)

    def _undo(self) -> None:
        if self._session is None:
            self.statusBar().showMessage("Open a PDF before using Undo.", 3000)
            return

        session, step = self._history.undo()
        if session is None or step is None:
            self.statusBar().showMessage("Nothing to undo.", 2500)
            return

        self._apply_history_session(session, step, action="undo")

    def _redo(self) -> None:
        if self._session is None:
            self.statusBar().showMessage("Open a PDF before using Redo.", 3000)
            return

        session, step = self._history.redo()
        if session is None or step is None:
            self.statusBar().showMessage("Nothing to redo.", 2500)
            return

        self._apply_history_session(session, step, action="redo")

    def _apply_history_session(
        self,
        session: DocumentSession,
        step: HistoryStep,
        action: str,
    ) -> None:
        self._session = session
        self._selected_page_indexes = [session.selected_page_index] if session.pages else []
        self._refresh_thumbnails(preserve_selection=True)
        if session.pages:
            self._thumbnail_panel.set_current_page(session.selected_page_index)
            self._select_page(session.selected_page_index)
        else:
            self._viewer_panel.show_placeholder(self.STARTUP_HINT)
            self._inspector_panel.set_blank_state()
        self._refresh_history_ui()
        self.statusBar().showMessage(
            f"{action.title()}: {step.label}",
            3000,
        )

    def _record_history_change(self, before: DocumentSession, label: str) -> None:
        if self._session is None:
            return

        if before == self._session:
            return

        self._history.record(self._session, label)
        self._refresh_history_ui()

    def _refresh_history_ui(self) -> None:
        self._toolbar.set_history_state(
            can_undo=self._history.can_undo,
            can_redo=self._history.can_redo,
        )
        self.setWindowTitle("PDF Viewer*" if self._history.is_dirty else "PDF Viewer")

    def _confirm_discard_unsaved_changes(self) -> bool:
        if not self._history.is_dirty:
            return True

        choice = QMessageBox.warning(
            self,
            "Discard unsaved changes?",
            "You have unsaved session changes. Continue and discard them?",
            QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        return choice == QMessageBox.StandardButton.Discard

    def _default_export_path(self) -> Path:
        if self._session is None:
            return Path.cwd() / "document.pdf"

        base_name = f"{self._session.source_path.stem}_edited.pdf"
        export_directory = self._settings_service.last_export_directory
        if export_directory is None:
            export_directory = self._session.source_path.parent
        return export_directory / base_name

    @staticmethod
    def _normalize_pdf_output_path(raw_output_path: str) -> Path:
        path = Path(raw_output_path)
        if path.suffix == "":
            return path.with_suffix(".pdf")
        return path

    def _run_export_task(self, label: str, callback: Callable[[], Path | list[Path]]):
        progress = QProgressDialog(label, "", 0, 0, self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setCancelButton(None)
        progress.setMinimumDuration(0)
        progress.show()
        QApplication.processEvents()
        try:
            return callback()
        finally:
            progress.close()

    def _confirm_overwrite(self, detail: str) -> bool:
        dialog = QMessageBox(self)
        dialog.setIcon(QMessageBox.Icon.Warning)
        dialog.setWindowTitle("Overwrite existing file?")
        dialog.setText("One or more export files already exist.")
        dialog.setInformativeText(detail)

        remember_choice = QCheckBox(
            "Always overwrite existing exports without prompting",
            dialog,
        )
        dialog.setCheckBox(remember_choice)
        overwrite_button = dialog.addButton("Overwrite", QMessageBox.ButtonRole.AcceptRole)
        dialog.addButton(QMessageBox.StandardButton.Cancel)
        dialog.setDefaultButton(QMessageBox.StandardButton.Cancel)
        dialog.exec()

        should_overwrite = dialog.clickedButton() == overwrite_button
        if should_overwrite and remember_choice.isChecked():
            self._settings_service.set_overwrite_existing(True)
        return should_overwrite

    def _show_export_error(self, title: str, message: str) -> None:
        QMessageBox.critical(self, title, message)
        self.statusBar().showMessage(f"{title}: {message}", 5000)

    def closeEvent(self, event) -> None:  # type: ignore[override]
        if self._confirm_discard_unsaved_changes():
            if self._session is None:
                self._settings_service.clear_last_session_path()
            event.accept()
            return
        event.ignore()
