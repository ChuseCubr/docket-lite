# Docket-lite

Docket-lite is a Python script that makes a dynamic schedule for [Conky](https://github.com/brndnmtthws/conky).

It's a less powerful version of [my Rainmeter skin](https://github.com/ChuseCubr/RM-Docket).

Here's a demo of the vertical layout:

![vertical_demo](https://user-images.githubusercontent.com/27886422/174424781-8b480dc9-7910-4dcb-9e37-fe7e779602d9.gif)

Here's a demo of the horizontal layout:

![horizontal_demo](https://user-images.githubusercontent.com/27886422/174424790-ac5fe546-944b-4f55-995f-4e8a258bcc39.gif)

## Table of Contents

* [Dependencies](#dependencies)
* [Installation](#installation)
* [Usage](#usage)
* [Configuration](#configuration)
* [License](#license)

## Dependencies

Of course, you're going to need [Conky](https://github.com/brndnmtthws/conky). If you don't already have it, you can check out its [wiki](https://github.com/brndnmtthws/conky/wiki/Installation).

The script itself is in [Python](https://www.python.org/), which is preinstalled on most distros.

If you're on an Ubuntu-based distro, like I am, they're both easy to install using `apt`:

```bash
sudo apt install conky
sudo apt install python3
```

## Installation

Download from the [releases tab](https://github.com/ChuseCubr/Docket-lite/releases) and unpack, or clone this repo:

```bash
git clone https://github.com/ChuseCubr/Docket-lite.git 
```

## Usage

Modify `schedule.csv` to your needs. See the example [schedule.csv](https://github.com/ChuseCubr/Docket-lite/blob/main/schedule.csv) for reference. 

* Times must be in a 24-hour format.
* If you'd like to use the ISO format (Sunday as the first day of the week), please see the configuration section.

Then run the `start_all.sh` script that will run terminals for:

1. Docket (script that will update the schedule conky)
1. A conky instance for the schedule
1. A conky instance for the weekday/week counter

Make sure to edit the path in the `start_all.sh`:

```bash
## start_all.sh
# change this to your install path
path_to_docket="$HOME/Docket-lite"
```

You can also run the Docket script on its own through `start.py`.

## Configuration

Configuration is done mainly through the main conky config (`conky-docket.conf` by default)

Here, you can configure the **script settings**:

```lua
--- conky-docket.conf
-- how often to check time (in seconds)
refresh = 5

-- first day of the week is sunday
iso_week = false
```
The **schedule layout**:

```lua
--- conky-docket.conf
-- stack subjects vertically
vertical_layout = true

-- spacing between subjects in vertical mode
vertical_spacing = 2

-- spacing between subjects in horizontal mode
horizontal_spacing = 200

-- only works in vertical mode
right_align = false
```

And the **schedule styles**:

```lua
--- conky-docket.conf
docket_styles = {
    upcoming_color  = '9999AA',
    ongoing_color   = 'DDEEFF',
    completed_color = '555577',

    upcoming_font   = 'Fira Sans:size=20',
    ongoing_font    = 'Fira Sans Bold:size=20',
    completed_font  = 'Fira Sans:size=20',

    time_color      = '777799',
    time_font       = 'Fira Sans:size=12',

    -- for positioning
    time_voffset    = -15,
    time_offset     = 3,
}
```

You can also configure the **file paths and toggle logging** through `start.py` using kwargs:

```python
# start.py
docket = Docket(
        conky_path = "conky-docket.conf",
        schedule_path = "schedule.csv",
        log_to_file = True,
        log_path = "docket.log")
```

The **week counter** can be configured in the week counter config (`conky-day.conf` by default):

```lua
--- conky-day.conf
-- change `-11` in `${execi 60 expr $(date +%V) + -11}` to suit your needs ---↴
conky.text = [[
${alignr}${color}${font Fira Sans:size=40}Week ${execi 60 expr $(date +%V) + -11}
${alignr}${voffset -30}${font Fira Sans:size=20}${time %A}
]]
```

## License

[MIT](https://choosealicense.com/licenses/mit/)
