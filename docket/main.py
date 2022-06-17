#!/usr/bin/env python3

from time import sleep

from docket.extras import Log, now_, today_
from docket.schedule import Schedule
from docket.conky import Conky

class Docket:
    def __init__(self, **kwargs):
        # moved into its own method for readability
        self._handle_kwargs(kwargs)

        try:
            self.refresh = float(self.conky.settings["refresh"])
        except:
            self.log.parse_warning("refresh", 5.0)
            self.refresh = 5.0

        self.log.info("Refresh period set to {}s".format(self.refresh))

    def start(self):
        try:
            while True:
                has_crossed_time_bound = False

                today = today_(self.is_isoweek)
                if not today == self.yesterday:
                    self.log.info("New day! Day: {}".format(today))
                    self.schedule.update_day(today)
                    has_crossed_time_bound =True
                self.yesterday = today

                while (len(self.schedule.time_bounds) > 0 and
                        now_() > self.schedule.time_bounds[0]):
                    crossed = self.schedule.time_bounds.pop(0)
                    self.log.info("Crossed time bound: " + crossed)
                    has_crossed_time_bound = True

                if has_crossed_time_bound:
                    self.schedule.update_status(now_())
                    self.conky.update_config(self.schedule.day)

                sleep(self.refresh)

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

        self.yesterday = (today_(self.is_isoweek) + 1) % 7
        if "schedule_path" in kwargs.keys():
            schedule_path = kwargs["schedule_path"]
            self.schedule = Schedule(self.log, self.yesterday, now_(), schedule_path)
        else:
            self.schedule = Schedule(self.log, self.yesterday, now_())

if __name__ == "__main__":
    docket = Docket()
    docket.start()
    pass
