#!/usr/bin/env python3

import re

from extras import log

class Conky:
    def __init__(self):
        log("Reading conky config...")
        with open("conky-docket.conf") as reader:
            self.lines = reader.readlines()

        self.refresh = 5
        self.parse_settings()

        self.text = []

    def parse_settings(self):
        log("Setting refresh period...")

        # look for settings variables
        for line in self.lines:
            # if past settings
            if line == "conky.config=[[\n":
                break

            if line.startswith("docket_refresh"):
                regex_pattern = "=(.*)\n"
                temp = re.search(regex_pattern, line)
                group = temp.group(1).strip(" '\"")
                log("Refresh period: " + group + "s")
                self.refresh = float(group)

    def update_config(self, sched):
        self._create_text(sched)
        self._write_config()
        pass

    def _create_text(self, sched):
        log("Generating conky.text...")

        # conky.text format:
        # ${colorN}${font name:size=size}Subj.name
        # ${colorN}${font name:size=size}Subj.start-Subj.end
        # <blank line>

        self.text = []
        first_run = True
        for subj in sched:
            if not first_run:
                self.text += ["\n"]

            self.text += ["${{color {color}}}${{font {font}}}{name}\n".format(
                    color = subj.status + "_color",
                    font = subj.status + "_font",
                    name = subj.name)]
            self.text += ["${{color time_color}}${{font time_font}}{start}-{end}\n".format(
                    start = subj.start,
                    end = subj.end)]
            first_run = False

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
        self.lines += self._substite_string()
        
        with open("conky-docket.conf", "w") as writer:
            writer.writelines(self.lines)

        log("conky config updated")

    def _substite_string(self):
        string = []
        settings = [
                "upcoming_color",
                "ongoing_color",
                "completed_color",
                "upcoming_font",
                "ongoing_font",
                "completed_font",
                "time_color",
                "time_font"
                ]

        for setting in settings:
            string += ["\nconky.text = conky.text:gsub(\"{setting}\", {setting})".format(setting = setting)]

        return string

if __name__ == "__main__":
    conky = Conky()
