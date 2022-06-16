#!/usr/bin/env python3

from time import sleep

from extras import Log, now_, today_
from schedule import Schedule
from conky import Conky

log = Log()

class Docket:
    def __init__(
            self,
            conky_path = "conky-docket.conf",
            schedule_path = "schedule.csv",
            log_path = "docket.log"):

        self.yesterday = (today_() + 1) % 7
        self.schedule = Schedule(self.yesterday, now_(), schedule_path)

        self.conky = Conky(conky_path)
        if not self.conky.settings["logging"] == "true":
            log.disable_file_logging()

        try:
            self.refresh = float(self.conky.settings["refresh"])
        except:
            self.refresh = 5

        log.info("Refresh period set to {}s".format(self.refresh))

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
                    log.info("Crossed time bound: " + crossed)
                    has_crossed_time_bound = True

                if has_crossed_time_bound:
                    log.debug("Updating conky config...")
                    self.schedule.update_status(now_())
                    self.conky.update_config(self.schedule.day)

                sleep(self.refresh)

        except KeyboardInterrupt:
            print("\ndocket: Received KeyboardInterrupt. Goodbye!")

if __name__ == "__main__":
    docket = Docket()
    docket.start()
    pass
