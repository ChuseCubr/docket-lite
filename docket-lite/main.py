#!/usr/bin/env python3

from time import sleep

from extras import log, parse_csv, now_, today_
from schedule import Schedule
from conky import Conky

def start():
    try:
        yesterday = (today_() + 1) % 7
        schedule = Schedule(parse_csv(), yesterday, now_())
        conky = Conky()
        try:
            refresh = float(conky.settings["refresh"])
        except:
            refresh = 5

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
                log("Crossed time bound: " + crossed)
                has_crossed_time_bound = True

            if has_crossed_time_bound:
                log("Updating conky config...")
                schedule.update_status(now_())
                conky.update_config(schedule.day)
                log("Refresh period set to {}s".format(refresh))

            sleep(refresh)

    except KeyboardInterrupt:
        print("\ndocket: Interrupted. Goodbye!")

if __name__ == "__main__":
    start()
    pass
