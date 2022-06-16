#!/usr/bin/env python3

import logging
log = logging.getLogger("docket")

class Subject:
    def __init__(self, name, start, end, now):
        self.name  = name
        self.start = start
        self.end  = end
        self.status = "upcoming"

        self.update_status(now)

    def update_status(self, now):
        if now < self.start:
            self.status = "upcoming"
        elif now > self.end:
            self.status = "completed"
        else:
            self.status = "ongoing"



class Schedule:
    def __init__(self, today, now):
        self.time_bounds = []
        self.week = []
        self.day = []

        raw_sched = self._parse_csv()
        self._init_week(raw_sched, now)
        self.update_day(today)

    def update_day(self, today):
        log.debug("Updating today's schedule...")
        self.day = []
        for row in self.week:
            self.day += [row[today]]

        log.debug("Compressing today's schedule...")
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
        log.debug("Updating subject statuses...")
        for subj in self.day:
            subj.update_status(now)



    ## private methods
    # file handling
    def _parse_csv(self):
        log.debug("Reading schedule spreadsheet...")
        raw_sched = []
        try:
            with open("schedulef.csv") as reader:
                lines = reader.readlines()
                for line in lines:
                    raw_sched += [line.replace("\n", "").split(",")]
                raw_sched.pop(0)

        except:
            log.error("Error while attempting to read schedule spreadsheet (./schedule.csv)")
            raise

        return raw_sched

    # data initialization
    def _init_week(self, raw_sched, now):
        log.debug("Converting schedule to object...")
        for raw_row in raw_sched:
            row = []
            for col in range(1, len(raw_row)):
                [start, end] = raw_row[0].split("-")
                row += [Subject(raw_row[col], start, end, now)]
                self.time_bounds += start, end
            self.week += [row]

        log.debug("Gathering time bounds...")
        filter = dict()
        for key in self.time_bounds:
            filter[key] = 0
        self.time_bounds = list(filter.keys())
        self.time_bounds.sort()
