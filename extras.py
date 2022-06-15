#!/usr/bin/env python3

from datetime import datetime

def log(text):
    print("docket: " + str(text))

def now_():
    return datetime.today().strftime("%H:%M")

def today_():
    return datetime.today().isoweekday()

def parse_csv():
    raw_sched = []
    with open("schedule.csv") as reader:
        log("Opening and reading schedule spreadsheet...")
        lines = reader.readlines()
        for line in lines:
            raw_sched += [line.replace("\n", "").split(",")]
    raw_sched.pop(0)
    return raw_sched
