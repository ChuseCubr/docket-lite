#!/usr/bin/env bash
# change this to your install path
path_to_docket="$HOME/Docket-lite"
cd $path_to_docket

x-terminal-emulator -e "python3 $path_to_docket/start.py" &

# wait for docket to write to file
sleep 1

x-terminal-emulator -e "conky -c $path_to_docket/conky-docket.conf" &

x-terminal-emulator -e "conky -c $path_to_docket/conky-day.conf"
