from pathlib import Path

import yaml

from log_viewer import LogViewer

if __name__ == "__main__":
    config = {}
    if Path("config.yml").exists():
        with open("config.yml", "r") as file:
            config = yaml.safe_load(file)
    if "file_default" in config:
        file_log = config["file_default"]
    else:
        file_log = ""
    app = LogViewer(file_log=file_log)
    app.run()
