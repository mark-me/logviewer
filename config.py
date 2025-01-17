from pathlib import Path
import tomllib

import toml

from logging_config import logging

logger = logging.getLogger(__name__)


class ConfigFile:
    def __init__(self, file_config: str):
        self._file = Path(file_config)
        self._data = {}
        self.lst_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
        self.dict_level_colors_defaults = {
            "ERROR": "red",
            "WARNING": "dark_orange",
            "INFO": "steel_blue3",
            "DEBUG": "grey62",
        }
        self._read_file()

    @property
    def file_default(self) -> str:
        return self._data["file_default"]

    @file_default.setter
    def file_default(self, value: str) -> None:
        if isinstance(value, Path):
            value = str(value)
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

    @property
    def level_colors(self) -> dict:
        return self._data["level_colors"]

    @level_colors.setter
    def level_colors(self, value: dict) -> None:
        if isinstance(value, dict):
            if all([level in value for level in self.lst_levels]):
                self._data["level_colors"] = value
            else:
                self._data["level_colors"] = self.dict_level_colors_defaults
        else:
            self._data["level_colors"] = self.dict_level_colors_defaults

    def _read_file(self):
        if Path(self._file).exists():
            logger.debug(f"Found config file '{self._file}'")
            with open(self._file, "rb") as file:
                self._data = tomllib.load(file)
            self._read_file_default()
            self._read_dir_default()
            self._read_level_colors()
        else:
            logger.warning(f"Found no config file '{self._file}'")

    def _read_dir_default(self):
        if "dir_default" not in self._data:
            logger.warning("Config file 'dir_default' not present")
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
            logger.warning("Config file 'file_default' not present")
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

    def _read_level_colors(self) -> None:
        if "level_colors" not in self._data:
            logger.warning("Config file 'level_colors' not present")
            self._data["level_colors"] = self.dict_level_colors_defaults
        elif not all(
            [level in self._data["level_colors"] for level in self.lst_levels]
        ):
            for k, v in self.dict_level_colors_defaults.items():
                if k not in self._data["level_colors"]:
                    logger.warning(f"Could not find color for '{k}', using default")
                    self._data["level_colors"][k] = v
        else:
            logger.debug("Config file 'level_colors' used")

    def _write_file(self) -> None:
        with open(self._file.stem + ".toml", "w") as f:
            toml.dump(self._data, f)
