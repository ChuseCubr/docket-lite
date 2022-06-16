#!/usr/bin/env python3

from time import sleep

from docket.extras import Log, now_, today_
from docket.schedule import Schedule
from docket.conky import Conky

class Docket:
    def __init__(self, **kwargs):
        if "conky_path" in kwargs.keys():
            conky_path = kwargs["conky_path"]
            self.conky = Conky(conky_path)
        else:
            self.conky = Conky()

        self.yesterday = (today_() + 1) % 7
        if "schedule_path" in kwargs.keys():
            schedule_path = kwargs["conky_path"]
            self.schedule = Schedule(self.yesterday, now_(), schedule_path)
        else:
            self.schedule = Schedule(self.yesterday, now_())

        if "log_path" in kwargs.keys():
            log_path = kwargs["conky_path"]
            self.log = Log(log_path)
        else:
            self.log = Log()

        if not self.conky.settings["logging"] == "true":
            self.log.disable_file_logging()

        try:
            self.refresh = float(self.conky.settings["refresh"])
        except:
            self.refresh = 5

        self.log.info("Refresh period set to {}s".format(self.refresh))

    def start(self):
        try:
            while True:
                has_crossed_time_bound = False
                today = today_()
                if not today == self.yesterday:
                    self.schedule.update_day(today)
                    has_crossed_time_bound =True
                self.yesterday = today

                while (len(self.schedule.time_bounds) > 0 and
                        now_() > self.schedule.time_bounds[0]):
                    crossed = self.schedule.time_bounds.pop(0)
                    self.log.info("Crossed time bound: " + crossed)
                    has_crossed_time_bound = True

                if has_crossed_time_bound:
                    self.log.debug("Updating conky config...")
                    self.schedule.update_status(now_())
                    self.conky.update_config(self.schedule.day)

                sleep(self.refresh)

        except KeyboardInterrupt:
            print("\ndocket: Received KeyboardInterrupt. Goodbye!")

if __name__ == "__main__":
    docket = Docket()
    docket.start()
    pass
