#!/usr/bin/env python3

import logging
from datetime import datetime

class Log:
    def __init__(self):
        # console logging always on
        self.logger = logging.getLogger("docket")
        self.logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch_formatter = logging.Formatter('%(name)s: %(levelname)s: %(message)s')
        ch.setFormatter(ch_formatter)
        self.logger.addHandler(ch)
        # file logging toggleable
        self.fh = logging.FileHandler("docket.log")
        self.fh.setLevel(logging.DEBUG)
        fh_formatter = logging.Formatter('[%(asctime)s] %(name)s - %(levelname)s: %(message)s')
        self.fh.setFormatter(fh_formatter)
        self.logger.addHandler(self.fh)

    def disable_file_logging(self):
        self.logger.removeHandler(self.fh)
        with open("conky-docket.conf", "w") as writer:
            writer.write("")

    # wrappers
    def info(self, text):
        self.logger.info(text)

    def debug(self, text):
        self.logger.debug(text)

    def error(self, text):
        self.logger.exception(text)

def now_():
    return datetime.today().strftime("%H:%M")

def today_():
    return datetime.today().isoweekday()
