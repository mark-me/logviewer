import json
import os
from pathlib import Path
import platform

from rich.text import Text
from textual import on
from textual.app import App, ComposeResult
from textual.containers import Grid, Horizontal, Vertical
from textual.widgets import Footer, Header, DataTable, Label, TextArea

from config import ConfigFile
from logging_config import logging
from open_dialog import OpenFileDialog

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
        self.config_file = config_file
        self.file_log = config_file.file_default
        self.dir_default = config_file.dir_default
        if self.file_log == "":
            self.sub_title = "No log file opened"
        else:
            self.sub_title = self.file_log
        self.tpl_log = ()
        self.tpl_table_headers = ()

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Grid(
            Header(),
            Horizontal(
                DataTable(id="table"),
                id="panel_table"
            ),
            Grid(
                Vertical(
                    Label("Level", id="label_levelname"),
                    Label("AscTime", id="label_asctime"),
                    Label("Module", id="label_module"),
                    Label("Function", id="label_funcName"),
                    id="bottom_left"
                ),
                TextArea("Message", language="markdown", id="label_message", read_only=True),
                id="panel_details"
            ),
            Footer(),
            id="app_grid"
        )

    def on_mount(self) -> None:
        if self.file_log == "":
            self.action_open_file()
        else:
            self.load_log(file_log=self.file_log)
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
            label_id= "#label_" + col
            if col == "message":
                self.query_one(label_id).load_text(value)
            elif col in ["levelname", "asctime"]:
                self.query_one(label_id).update(value)
            else:
                self.query_one(label_id).update(label_value)
        # Empty values
        for col in lst_col_missing:
            label_id= "#label_" + col
            self.query_one(label_id).update("")

    def load_log(self, file_log: str):
        """Loads the logfile"""
        log = []
        columns = ()
        colors_level = {
            "ERROR": "red",
            "WARNING": "dark_orange",
            "INFO": "steel_blue3",
            "DEBUG": "grey62",
        }
        if Path(file_log).exists():
            with open(file_log, "r") as file:
                logger.debug(f"Loading log file '{file_log}'")
                for line in file:
                    log_entry = json.loads(line)
                    columns = tuple(log_entry.keys())
                    entry = ()
                    for item in log_entry.items():
                        if item[0] == "levelname":
                            text = Text(item[1])
                            text.stylize(f"bold {colors_level[item[1]]}")
                            entry = entry + (text,)
                        else:
                            entry = entry + (item[1],)
                    log.append(entry)
            self.sub_title = self.file_log
            self.tpl_table_headers = columns
            log.reverse()
            self.tpl_log = log
        else:
            logger.error(f"Logfile '{file_log}' does not exist.")

    def populate_table(self) -> None:
        """Populates the DataTable"""
        table = self.query_one("DataTable")
        table = table.clear(columns=True)
        table.cursor_type = "row"
        table.zebra_stripes = True
        for col in self.tpl_table_headers:
            table.add_column(col, key=col)
        table.add_rows(self.tpl_log)
        self.query_one("DataTable").focus()

    def action_open_file(self) -> None:
        """Opens a file chooser dialog"""
        if self.dir_default == "":
            if "Windows" in platform.platform():
                dir_default = "C:/"
            else:
                dir_default = os.path.expanduser("~")
        else:
            dir_default = self.dir_default
        self.push_screen(
            OpenFileDialog(root=dir_default),
            self.open_file_dialog_callback,
        )

    def action_reload_log(self) -> None:
        logger.debug("Reloading log data")
        self.load_log(file_log=self.file_log)
        self.populate_table()
        self.notify(f"Reloaded the log file '{self.file_log}'")

    def open_file_dialog_callback(self, file: str) -> None:
        if file:
            self.notify(f"Opened file: '{file}'")
            self.file_log = file
            self.sub_title = file
            self.load_log(file_log=file)
            self.populate_table()
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

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def action_set_default_file(self) -> None:
        self.config_file.file_default = self.file_log