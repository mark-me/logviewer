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
            self._load_file()

    def _load_file(self) -> bool:
        """Loads the logfile"""
        success = False
        if self._file.exists():
            self._df_log = pd.read_json(self._file, orient="records", lines=True)
            self._df_log.sort_values(by="asctime", ascending=False, inplace=True)
            self._df_log["_selected"] = True
            success = True
        else:
            logger.error(f"Log file '{self._file}' does not exist")
        return success

    def load(self, file_log: str):
        self._file = Path(file_log)
        if not self._file.exists():
            self._file = ""
            logger.error(f"Log file '{self._file}' does not exist")
        else:
            self._load_file()

    def entries_formatted(self, level_colors: dict) -> list:
        lst_entries = []
        # Turn rows into tuples, taking only the runs that were selected
        df_selected = self._df_log[self._df_log["_selected"]]
        df_selected.drop("_selected", axis=1, inplace=True)
        lst_columns = list(df_selected.columns)
        for _, row in df_selected.iterrows():
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

    @property
    def runs(self) -> list:
        """Lists the runs present in the logfile (based on de process)

        Returns:
            list: _description_
        """
        lst_runs = []
        idx_runs_max = (
            self._df_log
            .groupby("process").asctime.idxmax()
        )
        df_runs = self._df_log.loc[idx_runs_max, ["process", "asctime"]]
        df_runs.sort_values(by="asctime", ascending=False, inplace=True)
        i = 0
        for _, row in df_runs.iterrows():
            lst_runs.append((row["asctime"], row["process"], i==0))
            i = i + 1
        return lst_runs

    def filter_runs(self, lst_runs: list) -> None:
        """_summary_

        Args:
            lst_runs (list): _description_

        Returns:
            _type_: _description_
        """
        self._df_log.loc[:, "_selected"] = self._df_log["process"].isin(lst_runs)

    def export(self, file: str, options: dict) -> bool:
        """Export the log to an Excel file, dropping rows and columns specified by options

        Args:
            file (str): The path of the Excel file
            options (dict): Specifies which columns should be dropped and what 'levelname' values should be dropped
        """
        df_export = self._df_log[self._df_log["_selected"]]
        df_export.drop("_selected", axis=1, inplace=True)
        if len(options["col_excludes"]) > 0:
            df_export.drop(options["col_excludes"], axis=1, inplace=True)
            pass
        if len(options["level_excludes"]) > 0:
            df_export = df_export.loc[~df_export['levelname'].isin(options["level_excludes"])]
        if df_export.shape[0] > 0:
            df_export.to_excel(file, index=False)

