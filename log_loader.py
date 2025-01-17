import json
from pathlib import Path

from rich.text import Text

from logging_config import logging

logger = logging.getLogger(__name__)

class LogLoader:
    def __init__(self, file_log: str):
        self._file = Path(file_log)
        if not self._file.exists():
            logger.error(f"Log file '{self._file}' does not exist")

    def load_log(self):
        """Loads the logfile"""
        log = []
        with open(self._file, "r") as file:
            logger.debug(f"Loading log file '{str(self._file)}'")
            for line in file:
                log_entry = json.loads(line)

                log.append(enlog_entrytry)


    def get_formatted(self) -> list:
        # columns = tuple(log_entry.keys())
        # entry = ()
        # for item in log_entry.items():
        #     if item[0] == "levelname":
        #         text = Text(item[1])
        #         text.stylize(f"bold {colors_level[item[1]]}")
        #         entry = entry + (text,)
        #     else:
        #         entry = entry + (item[1],)
        # self.sub_title = self.file_log
        # self.tpl_table_headers = columns
        # log.reverse()
        # self.tpl_log = log
        pass
