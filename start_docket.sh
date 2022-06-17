#!/usr/bin/env bash
path_to_docket="$HOME/Projects/Docket-lite"
cd $path_to_docket
x-terminal-emulator -e "python3 $path_to_docket/start.py" &
sleep 1
x-terminal-emulator -e "conky -c $path_to_docket/conky-docket.conf"
