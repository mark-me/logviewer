from pathlib import Path
import tomllib

import toml

from logging_config import logging

logger = logging.getLogger(__name__)


class ConfigFile:
    def __init__(self, file_config: str):
        self._file = Path(file_config)
        self._data = {}
        self._level_names = ["DEBUG", "INFO", "WARNING", "ERROR"]
        # TODO Create generic default dict
        level_colors = {
            "ERROR": "red",
            "WARNING": "dark_orange",
            "INFO": "steel_blue3",
            "DEBUG": "grey62",
        }
        self._defaults = {
            "level_colors": level_colors,
            "export_excludes": [],
            "file_default": "",
            "dir_default": "",
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
            if all([level in value for level in self._level_names]):
                self._data["level_colors"] = value
            else:
                self._data["level_colors"] = self._defaults["level_colors"]
        else:
            self._data["level_colors"] = self._defaults["level_colors"]

    def _read_file(self):
        if Path(self._file).exists():
            logger.debug(f"Found config file '{self._file}'")
            with open(self._file, "rb") as file:
                self._data = tomllib.load(file)
            self._read_path_str(setting="file_default")
            self._read_path_str(setting="dir_default")
            self._read_level_colors()
            self._read_list(setting="export_excludes")
        else:
            logger.warning(f"Found no config file '{self._file}'")

    def _read_path_str(self, setting: str) -> None:
        if setting not in self._data:
            logger.warning(f"Config file setting '{setting}' not present")
            self._data[setting] = ""
        else:
            if not Path(self._data[setting]).exists():
                logger.warning(
                    f"Path '{self._data[setting]}' does not exists for setting '{setting}'"
                )
                self._data[setting] = self._defaults[setting]
            else:
                logger.info(
                    f"Path '{self._data[setting]}' found for setting '{setting}'"
                )

    def _read_level_colors(self) -> None:
        setting = "level_colors"
        if setting not in self._data:
            logger.warning(f"Config file '{setting}' not present")
            self._data[setting] = self._defaults[setting]
        elif not all([level in self._data[setting] for level in self._level_names]):
            for k, v in self._defaults[setting].items():
                if k not in self._data[setting]:
                    logger.warning(f"Could not find color for '{k}', using default")
                    self._data[setting][k] = v
        else:
            logger.debug("Config file 'level_colors' used")

    def _read_list(self, setting: str) -> None:
        if setting not in self._data:
            logger.warning(f"Config file setting '{setting}' not present")
            self._data[setting] = []
        else:
            logger.debug(f"Settings found for {setting}")

    def _write_file(self) -> None:
        with open(self._file.stem + ".toml", "w") as f:
            toml.dump(self._data, f)
