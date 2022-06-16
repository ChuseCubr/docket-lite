#!/usr/bin/env python3

import re

import logging
log= logging.getLogger("docket")

class Conky:
    def __init__(self, path = "conky-docket.conf"):
        self.path = path
        self.lines = []
        self.settings = {
                "refresh": 5,
                "vertical_spacing": 2,
                "horizontal_spacing": 50,
                "vertical_layout": "true",
                "right_align": "false"
                }

        self._read_config()
        self._parse_settings()

    def update_config(self, sched):
        log.debug("Updating conky config...")
        self._create_text(sched)
        self._write_config()
        pass



    ## private methods
    # file handling
    def _read_config(self):
        log.debug("Reading conky config...")
        try:
            with open(self.path) as reader:
                self.lines = []
                for line in reader:
                    # ignore everything after conky.text line
                    if not re.search("^\s*conky.text\s*=\s*", line) == None:
                        break
                    self.lines += [line]

        except:
            log.error("Error occurred while attempting to read conky config ({})".format(self.path))
            raise

    def _write_config(self):
        log.debug("Writing to conky config...")
        try:
            with open(self.path, "w") as writer:
                writer.writelines(self.lines)
                writer.writelines(self.text)

            log.info("conky config updated")
        except:
            log.error("An error occurred while attempting to write conky config.")
            raise

    # file parsing
    def _parse_settings(self):
        settings = list(self.settings.keys())
        booleans = [
                "vertical_layout",
                "right_align"
                ]
        log.debug("Parsing settings...")

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

        for setting in booleans:
            self.settings[setting] = self.settings[setting] == "true"

    def _parse_setting(self, line, setting_name):
        # capture content
        regex_pattern = "\s*{}\s*=\s*(.+)\n"
        regex_pattern = regex_pattern.format(setting_name)
        temp = re.search(regex_pattern, line)

        # if not it, ignore
        if temp == None:
            return False

        group = temp.group(1).strip(" '\"")
        log.info("{}: {}".format(setting_name, group))
        self.settings[setting_name] = group
        return True

    # content generation
    def _create_text(self, sched):
        log.debug("Generating conky.text...")
        self.text = []

        # conky.text format:
        # ${colorN}${font name:size=size}Subj.name
        # ${colorN}${font name:size=size}Subj.start-Subj.end
        # <blank line>

        try:
            vertical_spacing = int(self.settings["vertical_spacing"])
        except:
            vertical_spacing = 2

        self.text = ["conky.text = [[\n"]

        # for vertical spacing between subjects
        first_run = True
        for subj in sched:
            if not first_run:
                for _ in range(vertical_spacing):
                    self.text += ["\n"]

            if self.settings["right_align"]:
                self.text += ["${alignr}"]
            self.text += ["${{color {}}}".format(subj.status + "_color")]
            self.text += ["${{font {}}}" .format(subj.status + "_font")]
            self.text += ["{}\n"    .format(subj.name)]
            if self.settings["right_align"]:
                self.text += ["${alignr}"]
            self.text += ["${voffset time_voffset}"]
            self.text += ["${offset time_offset}"]
            self.text += ["${color time_color}"]
            self.text += ["${font time_font}"]
            self.text += ["{}-{}\n".format(subj.start, subj.end)]

            first_run = False

        # make lua handle the string substitution here
        self.text += ["]]\n\nconky.text = insert_styles(conky.text, docket_styles)"]
