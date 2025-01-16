from pathlib import Path
import tomllib

import toml

from logging_config import logging

logger = logging.getLogger(__name__)


class ConfigFile:
    def __init__(self, file_config: str):
        self._file = Path(file_config)
        self._data = {}
        self._read_file()

    @property
    def file_default(self) -> str:
        return self._data["file_default"]

    @file_default.setter
    def file_default(self, value: str) -> None:
        if Path(value).exists():
            self._data["file_default"] = value
            self._write_file()
        else:
            logger.warning(f"File '{value}' does not exist")

    @property
    def dir_default(self) -> str:
        return self._data["dir_default"]

    @dir_default.setter
    def dir_default(self, value: str) -> None:
        if Path(value).exists():
            self._data["dir_default"] = value
            self._write_file()
        else:
            logger.warning(f"Dir '{value}' does not exist")

    def _read_file(self):
        if Path(self._file).exists():
            logger.debug(f"Found config file '{self._file}'")
            with open(self._file, "rb") as file:
                self._data = tomllib.load(file)
            self._read_file_default()
            self._read_dir_default()
        else:
            logger.warning(f"Found no config file '{self._file}'")

    def _read_dir_default(self):
        if "dir_default" not in self._data:
            self._data["dir_default"] = ""
        else:
            if not Path(self._data["dir_default"]).exists():
                logger.warning(
                    f"Config default directory '{self._data['dir_default']}' does not exist"
                )
                self._data["dir_default"] = ""
            else:
                logger.info(
                    f"Found config default directory '{self._data['dir_default']}'"
                )

    def _read_file_default(self) -> None:
        if "file_default" not in self._data:
            self._data["file_default"] = ""
        else:
            if not Path(self._data["file_default"]).exists():
                logger.warning(
                    f"Config default file '{self._data['file_default']}' does not exist"
                )
                self._data["file_default"] = ""
            else:
                logger.info(
                    f"Found config default log file '{self._data['file_default']}'"
                )

    def _write_file(self) -> None:
        with open(self._file.stem + ".toml", "w") as f:
            toml.dump(self._data, f)
