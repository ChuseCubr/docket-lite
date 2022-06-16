#!/usr/bin/env python3

import logging
from datetime import datetime

class Log:
    def __init__(self, log_to_file = False):
        logger = logging.getLogger("docket")
        logger.setLevel(logging.DEBUG)
        # create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(logging.ERROR)
        # create formatter and add it to the handlers
        ch_formatter = logging.Formatter('%(name)s: %(levelname)s: %(message)s')
        ch.setFormatter(ch_formatter)
        # add the handlers to logger
        logger.addHandler(ch)
        if log_to_file:
            # create file handler that logs debug and higher level messages
            fh = logging.FileHandler("docket.log")
            fh.setLevel(logging.DEBUG)
            fh_formatter = logging.Formatter('[%(asctime)s] %(name)s - %(levelname)s: %(message)s')
            fh.setFormatter(fh_formatter)
            logger.addHandler(fh)

    def info(self, text):
        logging.info(text)

    def debug(self, text):
        logging.debug(text)

def now_():
    return datetime.today().strftime("%H:%M")

def today_():
    return datetime.today().isoweekday()

