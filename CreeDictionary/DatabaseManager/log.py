import logging
import sys
from logging.handlers import TimedRotatingFileHandler
from os import mkdir
from os.path import isdir, dirname
from pathlib import Path

LOGGING_DIR = Path(dirname(__file__)) / "logs"
if not isdir(LOGGING_DIR):
    mkdir(LOGGING_DIR)
FORMATTER = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")
LOG_FILE = LOGGING_DIR / "DatabaseManager.log"


def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    return console_handler


def get_file_handler():
    file_handler = TimedRotatingFileHandler(LOG_FILE, when="midnight")
    file_handler.setFormatter(FORMATTER)
    return file_handler


class DatabaseManagerLogger(logging.Logger):
    def __init__(self, name: str, print_info_on_console: bool = True):
        super().__init__(name)
        self.setLevel(logging.DEBUG)  # better to have too much log than not enough
        self._console_handler = get_console_handler()
        self.addHandler(self._console_handler)
        self._file_handler = get_file_handler()
        self.addHandler(self._file_handler)
        # with this pattern, it's not necessary to propagate the error up to parent
        self.propagate = False

        self.set_print_info_on_console(print_info_on_console)

    def set_print_info_on_console(self, value: bool):
        if value:
            self._console_handler.setLevel(logging.INFO)
        else:
            self._console_handler.setLevel(logging.WARN)
