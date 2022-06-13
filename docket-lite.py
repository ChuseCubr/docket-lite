#!/usr/bin/env python3

from time import sleep
from datetime import datetime

today = datetime.today().isoweekday()

def parse_csv():
    raw_sched = []
    with open("schedule.csv") as reader:
        lines = reader.readlines()
        for line in lines:
            raw_sched += [line.replace("\n", "").split(",")]
    raw_sched.pop(0)
    return raw_sched

class Subject:
    def __init__(self, name, start, end):
        self.name  = name
        self.start = start
        self.stop  = end
        self.status = "upcoming"

class Schedule:
    def __init__(self, raw_sched):
        self.time_bounds = []
        self.week = []
        self.day = []

        self._init_week(raw_sched)
        self.update_day()
    
    def _init_week(self, raw_sched):
        # convert raw sched table to table of objects
        for raw_row in raw_sched:
            row = []
            for col in range(1, len(raw_row)):
                [start, end] = raw_row[0].split("-")
                row += [Subject(raw_row[col], start, end)]
                self.time_bounds += start, end
            self.week += [row]

        # quick and dirty unique filtering for time bounds
        filter = dict()
        for key in self.time_bounds:
            filter[key] = 0
        self.time_bounds = list(filter.keys())


    def update_day(self):
        # get today's subjects
        self.day = []
        for row in self.week:
            self.day += [row[today]]

        # remove blanks
        col = 0
        while col < len(self.day):
            if self.day[col].name == "":
                self.day.pop(col)
            else:
                col += 1

        # merge continuous
        col = 0
        while col < len(self.day)-1:
            if (self.day[col].name == self.day[col+1].name and
                    self.day[col].end == self.day[col+1].start):
                self.day[col].end = self.day[col+1].end
                self.day.pop(col+1)
            else:
                col += 1
    # TODO: update status property of subjects in sched.day
    def update_status(self):
        pass

    # TODO: write .conkyrc
    # TODO: "server" to keep checking time (with goodbye message hehe)

raw_sched = parse_csv()
sched = Schedule(raw_sched)
print(sched.week[0][1].name)
print(sched.day[2].name)
print(sched.time_bounds)

def main():
    while True:
        today = datetime.today().strftime("%A")
        print(today)
        sleep(3)
