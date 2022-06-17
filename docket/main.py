#!/usr/bin/env python3

from time import sleep
from datetime import datetime

from docket.log import Log
from docket.schedule import Schedule
from docket.conky import Conky

class Docket:
    def __init__(self, **kwargs):
        # moved into its own method for readability
        self._handle_kwargs(kwargs)
        self.log.info("Refresh period set to {}s".format(self.conky.settings["refresh"]))

    def start(self):
        try:
            while True:
                has_crossed_time_bound = False

                # update sched and config on new day
                today = self._today()
                if not today == self.yesterday:
                    self.log.info("New day! Today is ".format(self._weekday))
                    self.schedule.update_day(today)
                    has_crossed_time_bound =True
                self.yesterday = today

                # update config upon crossing time bound
                while (len(self.schedule.time_bounds) > 0 and
                        self._now() > self.schedule.time_bounds[0]):
                    crossed = self.schedule.time_bounds.pop(0)
                    self.log.info("Crossed time bound: " + crossed)
                    has_crossed_time_bound = True

                # update subj status and config
                if has_crossed_time_bound:
                    self.schedule.update_status(self._now())
                    self.conky.update_config(self.schedule.day)

                sleep(self.conky.settings["refresh"])

        except KeyboardInterrupt:
            print("\ndocket: Received KeyboardInterrupt. Goodbye!")



    # private methods
    def _handle_kwargs(self, kwargs):
        if "log_to_file" in kwargs.keys():
            log_to_file = kwargs["log_to_file"]
        else:
            log_to_file = False

        if "log_path" in kwargs.keys():
            log_path = kwargs["log_path"]
            self.log = Log(log_to_file, log_path)
        else:
            self.log = Log()

        if "conky_path" in kwargs.keys():
            conky_path = kwargs["conky_path"]
            self.conky = Conky(self.log, conky_path)
        else:
            self.conky = Conky(self.log)

        self.is_isoweek = self.conky.settings["iso_week"]

        self.yesterday = (self._today() + 6) % 7
        if "schedule_path" in kwargs.keys():
            schedule_path = kwargs["schedule_path"]
            self.schedule = Schedule(self.log, self.yesterday, self._now(), schedule_path)
        else:
            self.schedule = Schedule(self.log, self.yesterday, self._now())

    # macros / wrappers? Idk what these are called, I don't like typing
    def _now(self):
        return datetime.today().strftime("%H:%M")

    def _weekday(self):
        return datetime.today().strftime("%A")

    def _today(self):
        if self.is_isoweek:
            return datetime.today().isoweekday()
        return datetime.today().weekday()

if __name__ == "__main__":
    docket = Docket()
    docket.start()
    pass
