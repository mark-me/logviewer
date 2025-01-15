from pathlib import Path

import yaml

from log_viewer import LogViewer
from logging_config import logging

logger = logging.getLogger(__name__)

def read_config():
    config = {}
    if Path("config.yml").exists():
        logger.debug("Found config file 'config.yml'")
        with open("config.yml", "r") as file:
            config = yaml.safe_load(file)
    else:
        logger.warning("Found no config file 'config.yml'")
    if "file_default" not in config:
        config["file_default"] = ""
    else:
        if not Path(config["file_default"]).exists():
            logger.warning(f"Config default file '{config["file_default"]}' does not exist")
            config["file_default"] = ""
        else:
            logger.info(f"Found config default log file '{config["file_default"]}'")
    if "dir_default" not in config:
        config["dir_default"] = ""
    else:
        if not Path(config["dir_default"]).exists():
            logger.warning(f"Config default directory '{config["dir_default"]}' does not exist")
            config["dir_default"] = ""
        else:
            logger.info(f"Found config default directory '{config["dir_default"]}'")
    return config


if __name__ == "__main__":
    config = read_config()
    app = LogViewer(file_log=config["file_default"], dir_default=config["dir_default"])
    app.run()
