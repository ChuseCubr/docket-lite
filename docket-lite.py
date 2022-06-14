#!/usr/bin/env python3

import re
from time import sleep
from datetime import datetime

today = datetime.today().isoweekday()

# TODO: Logging

def parse_csv():
    raw_sched = []
    with open("schedule.csv") as reader:
        print("Opening and reading schedule spreadsheet...")
        lines = reader.readlines()
        for line in lines:
            raw_sched += [line.replace("\n", "").split(",")]
    raw_sched.pop(0)
    print("Schedule parsed")
    return raw_sched

class Subject:
    def __init__(self, name, start, end):
        self.name  = name
        self.start = start
        self.end  = end
        self.status = "1"

class Schedule:
    def __init__(self, raw_sched):
        self.time_bounds = []
        self.week = []
        self.day = []

        self._init_week(raw_sched)
        self.update_day()
    
    def _init_week(self, raw_sched):
        print("Converting schedule to object...")
        # convert raw sched table to table of objects
        for raw_row in raw_sched:
            row = []
            for col in range(1, len(raw_row)):
                [start, end] = raw_row[0].split("-")
                row += [Subject(raw_row[col], start, end)]
                self.time_bounds += start, end
            self.week += [row]
        print("Week schedule created")

        print("Gathering time bounds...")
        # quick and dirty unique filtering for time bounds
        filter = dict()
        for key in self.time_bounds:
            filter[key] = 0
        self.time_bounds = list(filter.keys())
        print("Time bounds gathered")


    def update_day(self):
        print("Updating today's schedule...")
        # get today's subjects
        self.day = []
        for row in self.week:
            self.day += [row[today]]

        print("Compressing...")
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

        print("Today's schedule updated")

    def update_status(self):
        print("Updating subject statuses")
        now = datetime.today().strftime("%H:%M")
        for subj in self.day:
            if now < subj.start:
                subj.status = "1"
            elif now > subj.end:
                subj.status = "3"
            else:
                subj.status = "2"

# TODO: Extract settings for generating conky.text

def read_conky():
    print("Reading conky config...")
    lines = []
    with open("conky-docket.conf") as reader:
        lines = reader.readlines()

    print("Parsing settings (fonts)...")
    settings = {
            "l_font": "",
            "t_font": ""
            }
    for line in lines:
        if ((not settings["l_font"] == []) 
                and (not settings["t_font"] == [])):
            break
        if settings["l_font"] == None:
            buffer = re.search('^\s*l_font\s*=\s*"(.*)",\n', line)
            if buffer == None:
                settings["l_font"] = ""
            else:
                print("Label font: " + buffer.group())
                settings["l_font"] = buffer.group()
        if settings["t_font"] == None:
            buffer = re.search('^\s*u_font\s*=\s*"(.*)",\n', line)
            if buffer == None:
                settings["t_font"] = ""
            else:
                print("Time font: " + buffer.group())
                settings["t_font"] = buffer.group()

    return lines, settings

# TODO: make conky.text

# conky.text format:
# ${colorN}${font name:size=size}Subj.name
# ${colorN}${font name:size=size}Subj.start-Subj.end

def create_conky_text(sched, settings):
    print("Generating conky.text...")
    conky_text = []
    for subj in sched:
        conky_text += ["${{color{status}}}${{font {font}}}{name}\n".format(
                status = subj.status,
                font = settings["l_font"],
                name = subj.name)]
        conky_text += ["${{color4}}${{font {font}}}{start}-{end}\n".format(
                status = subj.status,
                font = settings["t_font"],
                start = subj.start,
                end = subj.end)]
        conky_text += ["\n"]

    print("conky.text generated")
    return conky_text

# TODO: "server" to keep checking time (with goodbye message hehe)

def write_conky(lines, new_lines):
    print("Writing to conky config...")
    idx = lines.index("conky.text = [[\n") + 1
    # replace overlap
    while (idx < len(lines) and
            len(new_lines) > 0):
        lines[idx] = new_lines.pop(0)
        idx += 1
    # delete old excess
    while len(lines) > idx:
        lines.pop()
    # append new excess
    for item in new_lines:
        lines += [item]
    lines += ["]]"]
    
    with open("conky-docket.conf", "w") as writer:
        writer.writelines(lines)

    print("Conky config updated")

raw_sched = parse_csv()
sched = Schedule(raw_sched)
lines, settings = read_conky()
conky_text = create_conky_text(sched.day, settings)
write_conky(lines, conky_text)

def main():
    while True:
        today = datetime.today().strftime("%A")
        print(today)
        sleep(3)
