#!/usr/bin/env python3

from datetime import datetime
import logging

class Log:
    def __init__(self, log_to_file = True, path = "docket.log"):
        self.logger = logging.getLogger("docket")
        self.logger.setLevel(logging.DEBUG)

        # console logging always on
        self._create_console_handler()

        # file logging toggleable
        if log_to_file:
            self._create_file_handler(path)

    # wrappers
    def info(self, text):
        self.logger.info(text)

    def debug(self, text):
        self.logger.debug(text)

    def error(self, text):
        self.logger.exception(text)



    def _create_console_handler(self):
        # create handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # format handler
        ch_formatter = logging.Formatter('%(name)s: %(levelname)s: %(message)s')
        ch.setFormatter(ch_formatter)
        self.logger.addHandler(ch)

    def _create_file_handler(self, path):
        # create handler
        self.fh = logging.FileHandler(path)
        self.fh.setLevel(logging.DEBUG)

        # format handler
        fh_formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
        self.fh.setFormatter(fh_formatter)
        self.logger.addHandler(self.fh)

def now_():
    return datetime.today().strftime("%H:%M")

def today_():
    return datetime.today().isoweekday()
