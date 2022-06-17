#!/usr/bin/env python3

from docket.main import Docket

## Paths for each involved file can be set through kwargs
# conky_path = "conky-docket.conf"
# schedule_path = "schedule.csv"
# log_path = "docket.log"
# docket = Docket(
#         conky_path = conky_path,
#         schedule_path = schedule_path,
#         log_path = log_path)

docket = Docket()
docket.start()
