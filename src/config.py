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
        colors = ["grey62", "steel_blue3", "dark_orange", "red"]
        self._defaults = {
            "level_colors": dict(zip(self._level_names, colors)),
            "export":{
                "level_excludes": ["DEBUG", "INFO"],
                "col_excludes": [],
            },
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
        self._write_file()

    @property
    def export_options(self) -> dict:
        return self._data["export"]

    @property
    def export_col_excludes(self) -> list:
        return self._data["export"]["col_excludes"]

    @export_col_excludes.setter
    def export_col_excludes(self, value: list) -> None:
        self._data["export"]["col_excludes"] = value
        self._write_file()

    @property
    def export_level_excludes(self) -> list:
        return self._data["export"]["level_excludes"]

    @export_level_excludes.setter
    def export_level_excludes(self, value: list) -> None:
        self._data["export"]["level_excludes"] = value
        self._write_file()

    def _read_file(self):
        if Path(self._file).exists():
            logger.debug(f"Found config file '{self._file}'")
            with open(self._file, "rb") as file:
                self._data = tomllib.load(file)
            self._read_path_str(setting="file_default")
            self._read_path_str(setting="dir_default")
            self._read_dict(setting="level_colors")
            self._read_list(setting="col_excludes", section="export")
            self._read_list(setting="level_excludes", section="export")
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

    def _read_dict(self, setting: str, section: str=None) -> None:
        # Set default colors if not settings present
        if setting not in self._data:
            logger.warning(f"Config file '{setting}' not present")
            if section is None:
                self._data[setting] = self._defaults[setting]
            else:
                self._data[section][setting] = self._defaults[setting]
        # Add defaults if not all level colors where set
        elif not all([level in self._data[setting] for level in self._level_names]):
            levels_missing = [
                level
                for level in self._defaults[setting].keys()
                if level not in self._data[setting]
            ]
            for level in levels_missing:
                if section is None:
                    self._data[setting][level] = self._defaults[setting][level]
                else:
                    self._data[section][setting][level] = self._defaults[setting][level]
        # Everything is present in the configuration file
        else:
            logger.debug("Config file 'level_colors' used")

    def _read_list(self, setting: str, section: str=None) -> None:
        if section is None:
            if setting not in self._data:
                logger.warning(f"Config file setting '{setting}' not present")
                self._data[setting] = self._defaults[setting]
        else:
            if section in self._data:
                if setting not in self._data[section]:
                    logger.warning(f"Config file setting '{setting}' not present in '{section}'")
                    self._data[section][setting] = self._defaults[section][setting]
            else:
                logger.warning(f"Config file section '{section}' not present")
                self._data[section] = {}
                self._data[section][setting] = self._defaults[section][setting]

    def _write_file(self) -> None:
        with open(self._file.stem + ".toml", "w") as f:
            toml.dump(self._data, f)
