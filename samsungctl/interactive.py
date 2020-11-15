import curses

_wake_on_lan = '44:5C:E9:51:C8:29'
_mappings = [
    ["p",             "KEY_POWER",         "P",         "Power off"],
    ["h",             "KEY_HOME",          "H",         "Home"],
    ["KEY_UP",        "KEY_UP",            "Up",        "Up"],
    ["KEY_DOWN",      "KEY_DOWN",          "Down",      "Down"],
    ["KEY_LEFT",      "KEY_LEFT",          "Left",      "Left"],
    ["KEY_RIGHT",     "KEY_RIGHT",         "Right",     "Right"],
    ["\n",            "KEY_ENTER",         "Enter",     "Enter"],
    ["KEY_BACKSPACE", "KEY_RETURN",        "Backspace", "Return"],
    ["e",             "KEY_EXIT",          "E",         "Exit"],
    [" ",             "KEY_PLAY",          "Space",         "Play/Pause"],
    ["l",             "KEY_CH_LIST",       "L",         "Channel List"],
    ["m",             "KEY_MENU",          "M",         "Menu"],
    ["s",             "KEY_SOURCE",        "S",         "Source"],
    ["+",             "KEY_VOLUP",         "+",         "Volume Up"],
    ["-",             "KEY_VOLDOWN",       "-",         "Volume Down"],
    ["*",             "KEY_MUTE",          "*",         "Mute"],
    ["s",             "KEY_HDMI",          "S",        "HDMI Source"],
    ["i",             "KEY_INFO",          "I",        "Info"],
    ["n",             "KEY_MORE",          "D",        "Numbers"],
]


def run(remote):
    """Run interactive remote control application."""
    curses.wrapper(_control, remote)


def _control(std_scr, remote):
    height, width = std_scr.getmaxyx()

    std_scr.addstr("Interactive mode, press 'Q' to exit.\n")
    std_scr.addstr("Key mappings:\n")

    column_len = max(len(mapping[2]) for mapping in _mappings) + 1
    mappings_dict = {}
    for mapping in _mappings:
        mappings_dict[mapping[0]] = mapping[1]

        row = std_scr.getyx()[0] + 2
        if row < height:
            line = "  {}= {} ({})\n".format(mapping[2].ljust(column_len),
                                            mapping[3], mapping[1])
            std_scr.addstr(line)
        elif row == height:
            std_scr.addstr("[Terminal is too small to show all keys]\n")

    running = True
    while running:
        key = std_scr.getkey()

        if key == "q":
            running = False

        if key in mappings_dict:
            remote.control(mappings_dict[key])

            try:
                std_scr.addstr(".")
            except curses.error:
                std_scr.deleteln()
                std_scr.move(std_scr.getyx()[0], 0)
                std_scr.addstr(".")
