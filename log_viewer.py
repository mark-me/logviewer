import os

from rich.text import Text
from textual import on
from textual.app import App, ComposeResult
from textual.containers import Grid, Horizontal, Vertical
from textual.widgets import DataTable, Footer, Header, Label, TextArea

from config import ConfigFile
from dialog_export_selections import DialogExportOptions
from log_file import LogFile
from logging_config import logging
from dialog_open_log import DialogOpenLog
from dialog_export_log import DialogExportLog

logger = logging.getLogger(__name__)


class LogViewer(App):
    """Log viewer app"""

    DEFAULT_CSS = """
    #app_grid{
        grid-size: 1 4;
        grid-rows: 75% 25%;
        padding: 0 1;
        width: 100%;
        height: 100%;
    }

    #panel_details{
        grid-size: 2 1;
        grid-columns: auto 1fr;
        grid-gutter: 1;
        padding: 0 1;
        border: round gray;
        width: 100%;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("f", "open_file", "Open"),
        ("r", "reload_log", "Reload"),
        ("e", "export_file", "Export log"),
        ("a", "sort_by_asc_time", "Sort asctime"),
        ("d", "set_default_file", "Current log as default"),
        ("t", "toggle_dark", "Toggle dark mode"),
    ]

    current_sorts: set = set()

    def __init__(
        self,
        config_file: ConfigFile,
        driver_class=None,
        css_path=None,
        watch_css=False,
        ansi_color=False,
    ):
        super().__init__(driver_class, css_path, watch_css, ansi_color)
        self._config = config_file
        self._file_log = config_file.file_default
        self._dir_default = config_file.dir_default
        if self._file_log == "":
            self.sub_title = "No log file opened"
        else:
            self._log_file = LogFile(file_log=self._file_log)
            self.sub_title = self._file_log

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Grid(
            Header(),
            Horizontal(DataTable(id="table"), id="panel_table"),
            Grid(
                Vertical(
                    Label("Level", id="label_levelname"),
                    Label("AscTime", id="label_asctime"),
                    Label("Module", id="label_module"),
                    Label("Function", id="label_funcName"),
                    id="bottom_left",
                ),
                TextArea(
                    "Message", language="markdown", id="label_message", read_only=True
                ),
                id="panel_details",
            ),
            Footer(),
            id="app_grid",
        )

    def on_mount(self) -> None:
        if self._file_log == "":
            self.action_open_file()
        else:
            self.populate_table()

    @on(DataTable.RowHighlighted)
    @on(DataTable.RowSelected)
    def on_row_selected(self, message: DataTable.RowSelected) -> None:
        """
        Display selected log record details
        """
        # Get details for which values are present in log
        lst_col_details = ["asctime", "levelname", "message", "module", "funcName"]
        lst_col_log = [column.value for column in self.query_one("#table").columns]
        lst_col_present = list(set(lst_col_details) & set(lst_col_log))
        lst_col_missing = list(set(lst_col_details) - set(lst_col_log))
        for col in lst_col_present:
            value = self.query_one("#table").get_cell(message.row_key, col)
            if col not in ["levelname", "asctime"]:
                label_value = Text()
                label_value.append(col + ": ", style="bold")
                label_value.append(value)
            label_id = "#label_" + col
            if col == "message":
                self.query_one(label_id).load_text(value)
            elif col in ["levelname", "asctime"]:
                self.query_one(label_id).update(value)
            else:
                self.query_one(label_id).update(label_value)
        # Setting empty values for columns which are not in the log
        for col in lst_col_missing:
            label_id = "#label_" + col
            self.query_one(label_id).update("")

    def populate_table(self) -> None:
        """Populates the DataTable"""
        table = self.query_one("DataTable")
        table = table.clear(columns=True)
        table.cursor_type = "row"
        table.zebra_stripes = True
        self._log_file = LogFile(file_log=self._file_log)
        for col in self._log_file.headers:
            table.add_column(col, key=col)
        rows = self._log_file.entries_formatted(level_colors=self._config.level_colors)
        table.add_rows(rows)
        self.query_one("DataTable").focus()

    def action_open_file(self) -> None:
        """Opens a file chooser dialog"""
        if self._dir_default == "":
            dir_default = os.path.expanduser("~")
        else:
            dir_default = self._dir_default
        self.push_screen(
            DialogOpenLog(root=dir_default),
            self.dialog_callback_open_log,
        )

    def action_export_file(self) -> None:
        """Opens a file chooser dialog"""
        self.push_screen(
            DialogExportOptions(config=self._config, log_file=self._log_file),
            self.dialog_callback_export_options,
        )

    def action_reload_log(self) -> None:
        logger.debug("Reloading log data")
        self.populate_table()
        self.notify(f"Reloaded the log file '{self._file_log}'")

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )
        self.notify(f"Switched to theme '{self.theme}'")

    def action_set_default_file(self) -> None:
        self._config.file_default = self._file_log
        self.notify(f"Set '{self._file_log}' as default log file")

    def dialog_callback_open_log(self, file: str) -> None:
        if file:
            self.notify(f"Opened file: '{file}'")
            self._file_log = file
            self.sub_title = file
            self.populate_table()
        else:
            self.notify("You cancelled opening a file!")

    def dialog_callback_export_options(self, options: str) -> None:
        if options:
            self.push_screen(
                DialogExportLog(
                    root=self._config.dir_default,
                    log_file=self._log_file,
                    export_options=options,
                ),
                self.dialog_callback_export_log,
            )
        else:
            self.notify("You cancelled exporting a log!")

    def dialog_callback_export_log(self, file: str) -> None:
        if file:
            options = {
                "exclude_cols": self._config.export_col_excludes,
                "exclude_levels": self._config.export_level_excludes,
            }
            self._log_file.export(file=file, options=options)
            self.notify(f"Exporting file: '{file}'")

        else:
            self.notify("You cancelled opening a file!")

    def action_sort_by_asc_time(self) -> None:
        table = self.query_one(DataTable)
        table.sort(
            "asctime",
            key=lambda asctime: asctime,
            reverse=self.sort_reverse("asctime"),
        )

    def sort_reverse(self, sort_type: str):
        """Determine if `sort_type` is ascending or descending."""
        reverse = sort_type in self.current_sorts
        if reverse:
            self.current_sorts.remove(sort_type)
        else:
            self.current_sorts.add(sort_type)
        return reverse
