#!/usr/bin/env python3

from docket.main import Docket

## Paths for each involved file can be set through kwargs
# docket = Docket(
#         conky_path = "conky-docket.conf",
#         schedule_path = "schedule.csv",
#         log_to_file = True,
#         log_path = "docket.log")

docket = Docket()
docket.start()
