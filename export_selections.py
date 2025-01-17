import os

from textual import on
from textual.app import ComposeResult
from textual.containers import Grid, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Header, Label, RadioButton, Select

from config import ConfigFile
from log_file import LogFile
from logging_config import logging

logger = logging.getLogger(__name__)


class HeaderOptions(Horizontal):
    DEFAULT_CSS = """
    Column {
        height: 100%;
        margin: 0 2;
    }
    """

    def __init__(
        self,
        *children,
        columns: list,
        excludes: list,
        name=None,
        id=None,
        classes=None,
        disabled=False,
    ):
        super().__init__(
            *children, name=name, id=id, classes=classes, disabled=disabled
        )
        self._columns = columns
        self._excludes = excludes

    def compose(self) -> ComposeResult:
        for column in self._columns:
            is_excluded = column in self._excludes
            yield RadioButton(column, id=column, value=is_excluded)


class ExportOptions(ModalScreen):
    DEFAULT_CSS = """
    SaveFileDialog {
    align: center middle;
    background: $primary 30%;
    }

    #save_dialog{
        grid-size: 1 5;
        grid-gutter: 1 2;
        grid-rows: 5% 45% 30%;
        padding: 0 1;
        width: 100;
        height: 25;
        border: thick $background 70%;
        background: $surface-lighten-1;
    }

    #save_file {
        background: green;
    }
    """

    def __init__(
        self,
        config: ConfigFile,
        log_file: LogFile,
        root="/",
        columns: list = [],
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name, id, classes)
        self._log_file = log_file
        self._config = config
        self.title = "Export log errors/warnings"
        self._root = root
        self._folder = root

    def compose(self) -> ComposeResult:
        """
        Create the widgets for the SaveFileDialog's user interface
        """
        yield Grid(
            Header(),
            Label(f"Export options: {self._root}", id="folder"),
            Select(options=self._log_file.runs),
            HeaderOptions(
                columns=self._log_file.headers, excludes=self._config.export_excludes
            ),
            id="save_dialog",
        )

    def on_mount(self) -> None:
        """
        Focus the input widget so the user can name the file
        """
        pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Event handler for when the load file button is pressed
        """
        event.stop()
        if event.button.id == "save_file":
            filename = self.query_one("#filename").value
            full_path = os.path.join(self._folder, filename)
            self.dismiss(full_path)
        else:
            self.dismiss(False)
