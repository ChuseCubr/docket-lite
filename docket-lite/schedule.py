#!/usr/bin/env python3

from extras import log

class Subject:
    def __init__(self, name, start, end, now):
        self.name  = name
        self.start = start
        self.end  = end
        self.status = "0"

        self.update_status(now)

    def update_status(self, now):
        if now < self.start:
            self.status = "0"
        elif now > self.end:
            self.status = "2"
        else:
            self.status = "1"

class Schedule:
    def __init__(self, raw_sched, today, now):
        self.time_bounds = []
        self.week = []
        self.day = []

        self._init_week(raw_sched, now)
        self.update_day(today)

    def _init_week(self, raw_sched, now):
        log("Converting schedule to object...")
        # convert raw sched table to table of objects
        for raw_row in raw_sched:
            row = []
            for col in range(1, len(raw_row)):
                [start, end] = raw_row[0].split("-")
                row += [Subject(raw_row[col], start, end, now)]
                self.time_bounds += start, end
            self.week += [row]

        log("Gathering time bounds...")
        # quick and dirty unique filtering for time bounds
        filter = dict()
        for key in self.time_bounds:
            filter[key] = 0
        self.time_bounds = list(filter.keys())
        self.time_bounds.sort()


    def update_day(self, today):
        log("Updating today's schedule...")
        # get today's subjects
        self.day = []
        for row in self.week:
            self.day += [row[today]]

        log("Compressing today's schedule...")
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

    def update_status(self, now):
        log("Updating subject statuses...")
        for subj in self.day:
            subj.update_status(now)
