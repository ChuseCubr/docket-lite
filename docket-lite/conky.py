#!/usr/bin/env python3

import re

from extras import log

class Conky:
    def __init__(self):
        log("Reading conky config...")
        with open("conky-docket.conf") as reader:
            self.lines = []
            for line in reader:
                # ignore conky.text
                if line == "conky.text = [[\n":
                    break
                self.lines += line

        self.settings = {
                "refresh": 5,
                "log" : False
                }
        self.parse_settings()

        self.text = []

    def parse_settings(self):
        settings = list(self.settings.keys())
        log("Parsing settings...")

        # look for settings variables
        for line in self.lines:
            # if past settings
            if line == "docket_styles = {\n":
                break

            # if all settings set
            if (len(settings) == 0):
                break

            # check if it's a setting line
            i = 0
            while i < len(settings):
                found = self._parse_setting(line, settings[i])
                if found:
                    settings.pop(i)
                else:
                    i += 1

    def update_config(self, sched):
        self._create_text(sched)
        self._write_config()
        pass

    def _parse_setting(self, line, setting_name):
        # capture content
        regex_pattern = "\s*{}\s*=\s*(.*)\\n"
        regex_pattern = regex_pattern.format(setting_name)
        temp = re.search(regex_pattern, line)

        # if not it, ignore
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

        self.text = ["conky.text = [[\n"]
        first_run = True
        for subj in sched:
            if not first_run:
                self.text += ["\n\n"]

            self.text += ["${{color {color}}}${{font {font}}}{name}\n".format(
                    color = subj.status + "_color",
                    font = subj.status + "_font",
                    name = subj.name)]
            self.text += ["${{voffset time_voffset}}${{offset time_offset}}${{color time_color}}${{font time_font}}{start}-{end}\n".format(
                    start = subj.start,
                    end = subj.end)]
            first_run = False
        self.text += ["]]\n\nconky.text = insert_styles(conky.text, docket_styles)"]

    def _write_config(self):
        log("Writing to conky config...")

        # append new conky.text
        self.lines += self.text

        with open("conky-docket.conf", "w") as writer:
            writer.writelines(self.lines)

        log("conky config updated")

if __name__ == "__main__":
    conky = Conky()
