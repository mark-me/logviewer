import json
import os
import platform

from rich.text import Text
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, DataTable

from open_dialog import OpenFileDialog

class LogViewer(App):
    """Log viewer app"""

    BINDINGS = [
        ("f", "open_file", "Open file"),
        ("a", "sort_by_asc_time", "Sort asctime"),
        ("d", "toggle_dark", "Toggle dark mode"),
    ]

    current_sorts: set = set()

    def __init__(
        self, file_log: str="", driver_class=None, css_path=None, watch_css=False, ansi_color=False
    ):
        super().__init__(driver_class, css_path, watch_css, ansi_color)
        self.file_log = file_log
        self.tpl_log = ()
        self.tpl_table_headers = ()

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield DataTable(id="table")
        yield Footer()

    def on_mount(self) -> None:
        if self.file_log == "":
            self.action_open_file()
        else:
            self.load_log(file_log=self.file_log)
        self.populate_table()

    def load_log(self, file_log: str) -> tuple[list, tuple]:
        log = []
        columns = ()
        colors_level = {
            "ERROR": "red",
            "WARNING": "dark_orange",
            "INFO": "steel_blue3",
            "DEBUG": "grey62",
        }
        with open(file_log, "r") as file:
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
        log.reverse()
        self.tpl_table_headers = columns
        self.tpl_log = log

    def populate_table(self) -> None:
        table = self.query_one("DataTable")
        table = table.clear(columns=True)
        table.cursor_type = "row"
        table.zebra_stripes = True
        for col in self.tpl_table_headers:
            table.add_column(col, key=col)
        table.add_rows(self.tpl_log)
        self.query_one("DataTable").focus()

    def action_open_file(self) -> None:
        if "Windows" in platform.platform():
            self.push_screen(
                OpenFileDialog(root="C:/"),
                self.open_file_dialog_callback,
            )
        else:
            self.push_screen(
                OpenFileDialog(root=os.path.expanduser("~")),
                self.open_file_dialog_callback,
            )

    def open_file_dialog_callback(self, file: str) -> None:
        if file:
            self.notify(f"Opened file: '{file}'")
            self.file_log = file
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

