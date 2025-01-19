from config import ConfigFile
from log_viewer import LogViewer

if __name__ == "__main__":
    config_file = ConfigFile(file_config="config.toml")
    app = LogViewer(config_file=config_file)
    app.run()
