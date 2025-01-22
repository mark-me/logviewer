from textual import on
from textual.app import ComposeResult
from textual.containers import Grid, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Header, Label, RadioButton

from config import ConfigFile
from log_file import LogFile
from logging_config import logging

logger = logging.getLogger(__name__)


class SelectionList(Horizontal):
    def __init__(
        self,
        *children,
        values: list,
        excludes: list,
        name=None,
        id=None,
        classes=None,
        disabled=False,
    ):
        super().__init__(
            *children, name=name, id=id, classes=classes, disabled=disabled
        )
        self.values = values
        self.excludes = excludes

    def compose(self) -> ComposeResult:
        for value in self.values:
            is_included = value not in self.excludes
            yield RadioButton(value, id=value, value=is_included, classes="button")

    @on(RadioButton.Changed)
    def option_changed(self, message: RadioButton.Changed):
        value = message._toggle_button.id
        include = message.value
        if not include and value not in self.excludes:
            self.excludes.append(value)
        elif include and value in self.excludes:
            self.excludes.remove(value)


class DialogExportOptions(ModalScreen):
    DEFAULT_CSS = """
    DialogExportOptions {
    align: center middle;
    background: black 30%;
    }

    #export_options_dialog{
        grid-size: 1 4;
        grid-gutter: 1 2;
        grid-rows: 5% 1fr 1fr 15%;
        padding: 0 1;
        width: 110;
        height: 25;
        border: thick $background 70%;
        background: $surface-lighten-1;
    }

    #btns_dialog{
        align: right bottom;
    }

    #btn_file {
        background: green;
    }

    .box {
    height: 1fr;
    border: solid green;
    }
    """

    def __init__(
        self,
        config: ConfigFile,
        log_file: LogFile,
        root="/",
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
        level_names = ["DEBUG", "INFO", "WARNING", "ERROR"]
        levels_exclude = self._config.export_level_excludes
        cols_log = self._log_file.headers
        cols_exclude = self._config.export_col_excludes
        yield Grid(
            Header(),
            Label(f"Export options: {self._root}", id="folder"),
            Vertical(
                Label("Columns to include"),
                SelectionList(
                    values=cols_log, excludes=cols_exclude, id="exclude_cols"
                ),
                classes="box",
            ),
            Vertical(
                Label("Levels to include"),
                SelectionList(
                    values=level_names, excludes=levels_exclude, id="exclude_levels"
                ),
                classes="box",
            ),
            Horizontal(
                Button("Cancel", variant="error", id="btn_cancel"),
                Button("Next", variant="primary", id="btn_file"),
                id="btns_dialog",
            ),
            id="export_options_dialog",
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
        if event.button.id == "btn_file":
            cols_exclude = self.query_one("#exclude_cols").excludes
            levels_exclude = self.query_one("#exclude_levels").excludes
            self._config.export_col_excludes = cols_exclude
            self._config.export_level_excludes = levels_exclude
            dict_options = {
                "cols_exclude": cols_exclude,
                "levels_exclude": levels_exclude,
            }
            self.dismiss(dict_options)
        else:
            self.dismiss(False)
