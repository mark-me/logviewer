import os

from textual import on
from textual.app import ComposeResult
from textual.containers import Grid, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, DirectoryTree, Header, Input, Label, RadioSet

from config import ConfigFile
from log_file import LogFile
from logging_config import logging

logger = logging.getLogger(__name__)


class SaveFileDialog(ModalScreen):
    DEFAULT_CSS = """
    SaveFileDialog {
    align: center middle;
    background: $primary 30%;
    }

    #save_dialog{
        grid-size: 1 5;
        grid-gutter: 1 2;
        grid-rows: 5% 45% 15% 30%;
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
        columns: list=[],
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name, id, classes)
        self.title = "Export log errors/warnings"
        self._root = root
        self._folder = root
        self._columns = columns

    def compose(self) -> ComposeResave_dialog.pysult:
        """
        Create the widgets for the SaveFileDialog's user interface
        """
        yield Grid(
            Header(),
            Label(f"Export options: {self._root}", id="folder"),
            DirectoryTree(self._root, id="directory"),
            Input(placeholder="filename.txt", id="filename"),
            RadioSet(*self._columns
            ),
            Horizontal(
                Button("Save File", variant="primary", id="save_file"),
                Button("Cancel", variant="error", id="cancel_file"),
            ),
            id="save_dialog",
        )

    def on_mount(self) -> None:
        """
        Focus the input widget so the user can name the file
        """
        self.query_one("#filename").focus()

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

    @on(DirectoryTree.DirectorySelected)
    def on_directory_selection(self, event: DirectoryTree.DirectorySelected) -> None:
        """
        Called when the DirectorySelected message is emitted from the DirectoryTree
        """
        self._folder = event.path
        self.query_one("#folder").update(f"Folder name: {self._folder}")
