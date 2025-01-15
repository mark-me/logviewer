from pathlib import Path

import yaml

from log_viewer import LogViewer


def read_config():
    config = {}
    if Path("config.yml").exists():
        with open("config.yml", "r") as file:
            config = yaml.safe_load(file)
    if "file_default" not in config:
        config["file_default"] = ""
    else:
        if not Path(config["file_default"]).exists():
            config["file_default"] = ""
    if "dir_default" not in config:
        config["dir_default"] = ""
    else:
        if not Path(config["dir_default"]).exists():
            config["dir_default"] = ""
    return config


if __name__ == "__main__":
    config = read_config()
    app = LogViewer(file_log=config["file_default"], dir_default=config["dir_default"])
    app.run()
