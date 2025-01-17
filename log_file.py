from pathlib import Path

import pandas as pd
from rich.text import Text

from logging_config import logging

logger = logging.getLogger(__name__)


class LogFile:
    def __init__(self, file_log: str):
        self._file = Path(file_log)
        self._df_log = pd.DataFrame()
        self._levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
        if not self._file.exists():
            self._file = ""
            logger.error(f"Log file '{self._file}' does not exist")
        else:
            self.load_file()

    def load_file(self) -> bool:
        """Loads the logfile"""
        success = False
        if self._file.exists():
            self._df_log = pd.read_json(self._file, orient="records", lines=True)
            self._df_log.sort_values(by="asctime", ascending=False, inplace=True)
            success = True
        else:
            logger.error(f"Log file '{self._file}' does not exist")
        return success

    def entries_formatted(self, level_colors: dict) -> list:
        lst_entries = []
        lst_columns = list(self._df_log.columns)
        # Turn rows into tuples
        for index, row in self._df_log.iterrows():
            entry = ()
            for col in lst_columns:
                # Color levelname
                if col == "levelname":
                    levelname = Text(row[col])
                    levelname.style = f"bold {level_colors[row[col]]}"
                    entry = entry + (levelname,)
                else:
                    entry = entry + (row[col],)
            lst_entries.append(entry)
        return lst_entries

    @property
    def headers(self) -> tuple:
        headers = tuple(self._df_log.columns)
        return headers

    @property
    def entries(self) -> tuple:
        lst_entries = list(self._df_log.itertuples(index=False, name=None))
        return lst_entries
