#!/usr/bin/env python3

import re

from extras import log

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