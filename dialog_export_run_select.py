from textual.containers import Grid, Horizontal, Vertical
from textual.screen import ModalScreen

from log_file import LogFile
from logging_config import logging

logger = logging.getLogger(__name__)


class DialogSelectRun(ModalScreen):
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
        log_file: LogFile,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name, id, classes)
        self._log_file = log_file
        self.title = "Export log errors/warnings"

