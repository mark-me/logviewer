from textual.app import ComposeResult
from textual.containers import Grid, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Header, Label, SelectionList

from log_file import LogFile
from logging_config import logging

logger = logging.getLogger(__name__)


class DialogFilterRuns(ModalScreen):
    DEFAULT_CSS = """
    DialogSelectRun {
    align: center middle;
    background: black 30%;
    }

    #dialog_select_run{
        grid-size: 1 3;
        grid-gutter: 1 2;
        grid-rows: 5% 1fr 15%;
        padding: 0 1;
        width: 110;
        height: 25;
        border: thick $background 70%;
        background: $surface-lighten-1;
    }

    #btns_dialog{
        align: right bottom;
    }

    #btn_ok {
        background: green;
    }

    .box {
    height: 1fr;
    border: solid green;
    }
    """

    def __init__(
        self,
        log_file: LogFile,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name, id, classes)
        self._log_file = log_file
        self._lst_runs = self._log_file.runs
        self.title = "Export log errors/warnings"

    def compose(self) -> ComposeResult:
        """
        Create the widgets for the OpenFileDialog's user interface
        """
        lst_runs = self._lst_runs
        yield Grid(
            Header(),
            Label("Select the runs you want to include in the log selection"),
            SelectionList[int](*lst_runs, id="selection_run"),
            Horizontal(
                Button("Cancel", variant="error", id="btn_cancel"),
                Button("OK", variant="primary", id="btn_ok"),
                id="btns_dialog"
            ),
            id="dialog_select_run",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Event handler for when the load file button is pressed
        """
        event.stop()
        if event.button.id == "btn_ok":
            runs_include = self.query_one("#selection_run").selected
            self.dismiss(runs_include)
        else:
            self.dismiss(False)