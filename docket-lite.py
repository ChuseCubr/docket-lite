#!/usr/bin/env python3

import re
from time import sleep
from datetime import datetime

def main():
    try:
        yesterday = today_()
        schedule = Schedule(parse_csv(), yesterday)
        conky = Conky()

        try:
            refresh = int(conky.settings["docket_refresh"])
        except:
            refresh = 5

        while True:
            has_crossed_time_bound = False
            today = today_()
            if not today == yesterday:
                schedule.update_day(today)
            yesterday = today

            while (len(schedule.time_bounds) > 0 and
                    now_() > schedule.time_bounds[0]):
                crossed = schedule.time_bounds.pop(0)
                log("Crossed time bound: " + crossed)
                has_crossed_time_bound = True

            if has_crossed_time_bound:
                log("Updating conky config...")
                schedule.update_status()
                conky.update_config(schedule.day)

            sleep(refresh)

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

        settings = [
                "l_font",
                "t_font"
                ]

        for setting in settings:
            self.settings[setting] = ""

        # look for settings variables
        for line in self.lines:
            # if past settings
            if line == "conky.config=[[\n":
                break

            # if all settings set
            if (len(settings) == 0):
                break

            # check if it's a setting line
            i = 0
            while i < len(settings):
                found = self._parse_setting(line, settings[i])
                if found:
                    settings.remove(settings[i])
                else:
                    i += 1

    def update_config(self, sched):
        self._create_text(sched)
        self._write_config()
        pass

    def _parse_setting(self, line, setting_name):
        # ignore if not setting variable
        if not line.lstrip().startswith(setting_name):
            return False

        # capture content
        regex_pattern = "^.+?=(.*),\n$"
        temp = re.search(regex_pattern, line)

        if temp == None:
            return False

        group = temp.group(1).strip(" '\"")
        log(setting_name + ": " + group)
        self.settings[setting_name] = group
        return True

    def _create_text(self, sched):
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

    def _write_config(self):
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
    pass
