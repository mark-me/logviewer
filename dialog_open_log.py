from pathlib import Path
from typing import Iterable

from textual import on
from textual.app import ComposeResult
from textual.containers import Grid, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, DirectoryTree, Header, Label


class FilteredDirectoryTree(DirectoryTree):
    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        lst_extensions = [".json", ".log"] + ['.' + str(i) for i in range(50)]
        paths = [path for path in paths if not path.name.startswith(".")]
        paths = [path for path in paths if path.suffix in lst_extensions or path.is_dir()]
        return paths

class DialogOpenLog(ModalScreen):
    DEFAULT_CSS = """
    OpenFileDialog {
    align: center middle;
    background: $primary 30%;
    }

    #open_dialog{
        grid-size: 1 3;
        grid-gutter: 1 2;
        grid-rows: 5% 75% 1fr;
        padding: 0 1;
        width: 100;
        height: 25;
        border: thick $background 70%;
        background: $surface-lighten-1;
    }

    #btns_dialog{
        align: right bottom;
    }

    #open_file {
        background: green;
    }
    """

    def __init__(self, root="/") -> None:
        super().__init__()
        self.title = "Open log file"
        self.root = root
        self.folder = root
        self.file_selected = ""

    def compose(self) -> ComposeResult:
        """
        Create the widgets for the OpenFileDialog's user interface
        """
        yield Grid(
            Header(),
            Label(f"Folder name: {self.root}", id="folder"),
            FilteredDirectoryTree(self.root, id="directory"),
            Horizontal(
                Button("Cancel", variant="error", id="cancel_file"),
                Button("Open File", variant="primary", id="open_file", disabled=True),
                id="btns_dialog"
            ),
            id="open_dialog",
        )

    def on_mount(self) -> None:
        """
        Focus the input widget so the user can name the file
        """
        self.query_one("#directory").focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Event handler for when the load file button is pressed
        """
        event.stop()
        if event.button.id == "open_file":
            self.dismiss(self.file_selected)
        else:
            self.dismiss(False)

    @on(DirectoryTree.FileSelected)
    def handle_file_selected(self, message: DirectoryTree.FileSelected) -> None:
        """
        Do something with the selected file.

        Objects returned by the FileSelected event are upath.UPath objects and
        they are compatible with the familiar pathlib.Path API built into Python.
        """
        self.sub_title = str(message.path)
        self.query_one("#open_file").disabled=False
        self.file_selected = message.path

    @on(DirectoryTree.DirectorySelected)
    def on_directory_selection(self, event: DirectoryTree.DirectorySelected) -> None:
        """
        Called when the DirectorySelected message is emitted from the DirectoryTree
        """
        self.folder = event.path
        self.query_one("#folder").update(f"Folder: {self.folder}")
        self.query_one("#open_file").disabled=True
