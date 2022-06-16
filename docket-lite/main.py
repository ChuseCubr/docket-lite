#!/usr/bin/env python3

from time import sleep

from extras import Log, now_, today_
from schedule import Schedule
from conky import Conky

log = Log()

def start(
        conky_path = "conky-docket.conf",
        schedule_path = "schedule.csv"):

    yesterday = (today_() + 1) % 7
    schedule = Schedule(yesterday, now_(), schedule_path)

    conky = Conky(conky_path)
    if not conky.settings["logging"] == "true":
        log.disable_file_logging()

    try:
        refresh = float(conky.settings["refresh"])
    except:
        refresh = 5

    log.info("Refresh period set to {}s".format(refresh))

    server(conky, schedule, yesterday, refresh)

def server(conky, schedule, yesterday, refresh):
    try:
        while True:
            has_crossed_time_bound = False
            today = today_()
            if not today == yesterday:
                schedule.update_day(today)
                has_crossed_time_bound =True
            yesterday = today

            while (len(schedule.time_bounds) > 0 and
                    now_() > schedule.time_bounds[0]):
                crossed = schedule.time_bounds.pop(0)
                log.info("Crossed time bound: " + crossed)
                has_crossed_time_bound = True

            if has_crossed_time_bound:
                log.debug("Updating conky config...")
                schedule.update_status(now_())
                conky.update_config(schedule.day)

            sleep(refresh)

    except KeyboardInterrupt:
        print("\ndocket: Received KeyboardInterrupt. Goodbye!")

if __name__ == "__main__":
    start()
    pass
