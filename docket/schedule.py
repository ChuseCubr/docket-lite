#!/usr/bin/env python3

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
    def __init__(self, logger, today, now, path = "schedule.csv"):
        self.log = logger
        self.time_bounds = []
        self.week = []
        self.day = []

        raw_sched = self._parse_csv(path)
        self._init_week(raw_sched, now)
        self.update_day(today)

    def update_day(self, today):
        self.log.debug("Updating today's schedule...")
        self.day = []
        try:
            for row in self.week:
                self.day += [row[today]]
        except:
            self.log.error("Error while parsing schedule")
            self.log.error("Please make sure there are enough columns (try adding an extra comma in each row)")
            raise

        self.log.debug("Compressing today's schedule...")
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
        self.log.debug("Updating subject statuses...")
        for subj in self.day:
            subj.update_status(now)



    ## private methods
    # file handling
    def _parse_csv(self, path):
        self.log.debug("Reading schedule spreadsheet...")
        raw_sched = []
        try:
            with open(path) as reader:
                lines = reader.readlines()
                for line in lines:
                    raw_sched += [line.replace("\n", "").split(",")]
                raw_sched.pop(0)

        except:
            self.log.error("Error while attempting to read schedule spreadsheet ({})".format(path))
            raise

        return raw_sched

    # data initialization
    def _init_week(self, raw_sched, now):
        self.log.debug("Converting schedule to object...")
        for raw_row in raw_sched:
            row = []
            for i, item in enumerate(raw_row):
                if i == 0: continue
                try:
                    [start, end] = raw_row[0].split("-")
                except:
                    self.log.error("Error while parsing time column.")
                    self.log.error("Please make sure it's the proper format: HH:MM-HH:MM")
                    raise
                row += [Subject(item, start, end, now)]
                self.time_bounds += start, end
            self.week += [row]

        self.log.debug("Gathering time bounds...")
        filter = dict()
        for key in self.time_bounds:
            filter[key] = 0
        self.time_bounds = list(filter.keys())
        self.time_bounds.sort()
