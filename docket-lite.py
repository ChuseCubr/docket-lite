#!/usr/bin/env python3

import re
from time import sleep
from datetime import datetime

#  raw_sched = parse_csv()
#  sched = Schedule(raw_sched)
#  lines, settings = Conky.read_config()
#  conky_text = Conky.create_text(sched.day, settings)
#  Conky.update_config(lines, conky_text)

def main():
    try:
        yesterday = (today_() + 1) % 7
        schedule = Schedule(parse_csv(), yesterday)
        conky = Conky()

        while True:
            has_crossed_time_bound = False
            today = today_()
            if not today == yesterday:
                schedule.update_day(today)
            yesterday = today

            while (len(schedule.time_bounds) > 0 and
                    now_() > schedule.time_bounds[0]):
                schedule.time_bounds.pop(0)
                has_crossed_time_bound = True

            if has_crossed_time_bound:
                schedule.update_status()

            sleep(5)

    except KeyboardInterrupt:
        print("\ndocket: Interrupted. Goodbye!")

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

class Subject:
    def __init__(self, name, start, end):
        self.name  = name
        self.start = start
        self.end  = end
        self.status = "0"

        self.update_status(now_())

    def update_status(self, now):
        if now < self.start:
            self.status = "0"
        elif now > self.end:
            self.status = "2"
        else:
            self.status = "1"

class Schedule:
    def __init__(self, raw_sched, today):
        self.time_bounds = []
        self.week = []
        self.day = []

        self._init_week(raw_sched)
        self.update_day(today)

    def _init_week(self, raw_sched):
        log("Converting schedule to object...")
        # convert raw sched table to table of objects
        for raw_row in raw_sched:
            row = []
            for col in range(1, len(raw_row)):
                [start, end] = raw_row[0].split("-")
                row += [Subject(raw_row[col], start, end)]
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

    def update_status(self):
        log("Updating subject statuses...")
        now = now_()
        for subj in self.day:
            subj.update_status(now)

class Conky:
    def __init__(self):
        log("Reading conky config...")
        with open("conky-docket.conf") as reader:
            self.lines = reader.readlines()

        self.settings = {}
        self.parse_settings()

        self.text = []

    def parse_settings(self):
        log("Parsing settings (fonts)...")
        settings = {
                "l_font": "",
                "t_font": ""
                }

        # look for settings variables
        for line in self.lines:
            if ((not settings["l_font"] == []) 
                    and (not settings["t_font"] == [])):
                break

            if settings["l_font"] == None:
                buffer = re.search('^\s*l_font\s*=\s*"(.*)",\n', line)
                if buffer == None:
                    settings["l_font"] = ""
                else:
                    log("Label font: " + buffer.group())
                    settings["l_font"] = buffer.group()

            if settings["t_font"] == None:
                buffer = re.search('^\s*u_font\s*=\s*"(.*)",\n', line)
                if buffer == None:
                    settings["t_font"] = ""
                else:
                    log("Time font: " + buffer.group())
                    settings["t_font"] = buffer.group()

    def create_text(self, sched):
        log("Generating conky.text...")

        # conky.text format:
        # ${colorN}${font name:size=size}Subj.name
        # ${colorN}${font name:size=size}Subj.start-Subj.end
        # <blank line>

        self.text = []
        for subj in sched:
            self.text += ["${{color{status}}}${{font {font}}}{name}\n".format(
                    status = subj.status,
                    font = self.settings["l_font"],
                    name = subj.name)]

            self.text += ["${{color3}}${{font {font}}}{start}-{end}\n".format(
                    status = subj.status,
                    font = self.settings["t_font"],
                    start = subj.start,
                    end = subj.end)]

            self.text += ["\n"]

    def update_config(self):
        log("Writing to conky config...")
        idx = self.lines.index("conky.text = [[\n") + 1

        # replace overlap
        while (idx < len(self.lines) and
                len(self.text) > 0):
            self.lines[idx] = self.text.pop(0)
            idx += 1

        # delete old excess
        while len(self.lines) > idx:
            self.lines.pop()

        # append new excess
        for item in self.text:
            self.lines += [item]
        self.lines += ["]]"]
        
        with open("conky-docket.conf", "w") as writer:
            writer.writelines(self.lines)

        log("conky config updated")

if __name__ == "__main__":
    main()
