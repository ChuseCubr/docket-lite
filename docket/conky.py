#!/usr/bin/env python3

import re

class Conky:
    def __init__(self, logger, path = "conky-docket.conf"):
        self.log = logger
        self.path = path
        self.config = []
        self.settings = {
                "vertical_layout": "true",
                "right_align": "false",
                "iso_week": "false",
                "refresh": 5,
                "vertical_spacing": 2,
                "horizontal_spacing": 200,
                }

        self._read_config()
        self._parse_settings()
        self._set_settings()

    def update_config(self, sched):
        self.log.debug("Updating conky config...")
        self._create_text(sched)
        self._write_config()
        pass



    ## private methods
    # file handling
    def _read_config(self):
        self.log.debug("Reading conky config...")
        try:
            with open(self.path) as reader:
                self.config = []
                for line in reader:
                    # ignore everything after conky.text line
                    if not re.search("^\s*conky.text\s*=\s*", line) == None:
                        break
                    self.config += [line]
        except:
            self.log.error("Error occurred while attempting to read conky config ({})".format(self.path))
            raise

    def _write_config(self):
        self.log.debug("Writing to conky config...")
        try:
            with open(self.path, "w") as writer:
                writer.writelines(self.config)
                writer.write(self.text)

            self.log.info("conky config updated")
        except:
            self.log.error("An error occurred while attempting to write conky config.")
            raise

    ## settings processing
    # loop through config lines
    def _parse_settings(self):
        settings = list(self.settings.keys())
        self.log.debug("Parsing settings...")

        # look for settings variables
        for line in self.config:
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

    # parse each line for settings text
    def _parse_setting(self, line, setting_name):
        # capture content
        regex_pattern = "\s*{}\s*=\s*(.+)\n"
        regex_pattern = regex_pattern.format(setting_name)
        temp = re.search(regex_pattern, line)

        # if not it, ignore
        if temp == None:
            return False

        group = temp.group(1).strip(" '\"")
        self.log.info("{}: {}".format(setting_name, group))
        self.settings[setting_name] = group
        return True

    # convert settings text to actual types
    def _set_settings(self):
        booleans = [
                "vertical_layout",
                "right_align",
                "iso_week",
                ]
        for setting in booleans:
            self.settings[setting] = self.settings[setting] == "true"

        self._setting_to_int("vertical_spacing", 2)
        self._setting_to_int("horizontal_spacing", 200)
        self._setting_to_int("refresh", 5)

    # fallback values for numbers
    def _setting_to_int(self, setting_name, default):
        try:
            self.settings[setting_name] = int(self.settings[setting_name])
        except:
            self.log.parse_warning(setting_name, default)
            self.settings[setting_name] = default

    # content generation
    def _create_text(self, sched):
        self.log.debug("Generating conky.text...")
        self.text = "conky.text = [[\n"

        ## conky.text format:
        # ${color color}${font font}Subj.name
        # ${color color}${font font}Subj.start-Subj.end
        # <blank line>

        # vertical layout
        if self.settings["vertical_layout"]:
            first_run = True
            for subj in sched:
                if not first_run:
                    for _ in range(self.settings["vertical_spacing"]):
                        self.text += "\n"
                
                self._create_subject_text(subj)
                self.text += "\n"
                self.text += "${voffset time_voffset}"
                self._create_time_text(subj)
                self.text += "\n"

                first_run = False

        # horizontal layout
        else:
            if self.settings["right_align"] == True:
                self.log.warning("Right align cannot be enabled in horizontal mode")
                self.settings["right_align"] = False

            for i, subj in enumerate(sched):
                self.text += "${{goto {}}}".format(i * self.settings["horizontal_spacing"])
                self._create_subject_text(subj)

            self.text += "\n"
            self.text += "${voffset time_voffset}"

            for i, subj in enumerate(sched):
                self.text += "${{goto {}}}".format(i * self.settings["horizontal_spacing"])
                self._create_time_text(subj)
                
        # make lua handle the string substitution here
        self.text += "]]\n\n-- Apply label styles\nconky.text = insert_styles(conky.text, docket_styles)"

    # long, consistent text blocks that get rearranged
    def _create_subject_text(self, subj):
        if self.settings["right_align"]:
            self.text += "${alignr}"
        self.text += "${{color {}_color}}".format(subj.status)
        self.text += "${{font {}_font}}".format(subj.status)
        self.text += "{}".format(subj.name)
        pass
    
    def _create_time_text(self, subj):
        self.text += "${offset time_offset}"
        if self.settings["right_align"]:
            self.text += "${alignr}"
        self.text += "${color time_color}"
        self.text += "${font time_font}"
        self.text += "{}-{}".format(subj.start, subj.end)
        pass
