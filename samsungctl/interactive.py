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
    [" ",             "KEY_PLAY",          "Space",     "Play/Pause"],
    ["m",             "KEY_MENU",          "M",         "Menu"],
    ["s",             "KEY_SOURCE",        "S",         "Source"],
    ["+",             "KEY_VOLUP",         "+",         "Volume Up"],
    ["-",             "KEY_VOLDOWN",       "-",         "Volume Down"],
    ["*",             "KEY_MUTE",          "*",         "Mute"],
    ["d",             "KEY_HDMI",          "D",         "HDMI Source"],
    ["i",             "KEY_INFO",          "I",         "Info"],
    ["n",             "KEY_MORE",          "N",         "Numbers"],
]


def run(remote):
    """Run interactive remote control application."""
    curses.wrapper(_control, remote)


def _control(std_scr, remote):
    std_scr.keypad(True)
    mappings_dict = {mapping[0]: mapping[1] for mapping in _mappings}
    mappings_dict["\x7f"] = "KEY_RETURN"  # macOS backspace sends DEL (0x7f)

    pointer_mode = False
    pointer_step = 40
    _draw_help(std_scr)
    _show_status(std_scr, "Remote mode")

    while True:
        try:
            key = std_scr.getkey()
        except KeyboardInterrupt:
            break

        if key == "q":
            break
        elif key == "c":
            pointer_mode = not pointer_mode
            mode = "Cursor mode (step {})".format(pointer_step)
            _show_status(std_scr, mode if pointer_mode else "Remote mode")
        elif key == "t":
            text = _read_text(std_scr)
            if text is None:
                _show_status(std_scr, "Text input cancelled")
            elif text:
                remote.send_text(text)
                remote.end_text()
                _show_status(std_scr, "Sent {} character(s)".format(len(text)))
            else:
                _show_status(std_scr, "No text entered")
        elif pointer_mode:
            movements = {
                "KEY_UP": (0, -pointer_step),
                "KEY_DOWN": (0, pointer_step),
                "KEY_LEFT": (-pointer_step, 0),
                "KEY_RIGHT": (pointer_step, 0),
            }
            if key in movements:
                remote.move_cursor(*movements[key])
                _show_status(std_scr, "Cursor moved")
            elif key in ("\n", "KEY_ENTER", " "):
                remote.click_cursor("left")
                _show_status(std_scr, "Left click")
            elif key == "r":
                remote.click_cursor("right")
                _show_status(std_scr, "Right click")
            elif key == "+":
                pointer_step = min(pointer_step + 10, 200)
                _show_status(std_scr, "Cursor step: {}".format(pointer_step))
            elif key == "-":
                pointer_step = max(pointer_step - 10, 10)
                _show_status(std_scr, "Cursor step: {}".format(pointer_step))
        elif key in mappings_dict:
            remote.control(mappings_dict[key])
            _show_status(std_scr, "Sent {}".format(mappings_dict[key]))


def _draw_help(std_scr):
    height, width = std_scr.getmaxyx()
    lines = [
        "Interactive mode - q exits",
        "c = cursor mode, t = type text",
        "Cursor: arrows move, Enter/Space left-click, r right-click, +/- speed",
        "",
        "Remote key mappings:"
    ]

    column_len = max(len(mapping[2]) for mapping in _mappings) + 1
    for mapping in _mappings:
        lines.append("  {}= {} ({})".format(
            mapping[2].ljust(column_len), mapping[3], mapping[1]
        ))

    std_scr.erase()
    for row, line in enumerate(lines[:max(0, height - 1)]):
        try:
            std_scr.addnstr(row, 0, line, max(0, width - 1))
        except curses.error:
            break
    std_scr.refresh()


def _show_status(std_scr, message):
    height, width = std_scr.getmaxyx()
    try:
        std_scr.move(height - 1, 0)
        std_scr.clrtoeol()
        std_scr.addnstr(height - 1, 0, message, max(0, width - 1))
        std_scr.refresh()
    except curses.error:
        pass


def _read_text(std_scr):
    prompt = "Text (Enter sends, Esc cancels): "
    characters = []

    while True:
        height, width = std_scr.getmaxyx()
        available = max(0, width - len(prompt) - 1)
        visible = "".join(characters)[-available:] if available else ""
        _show_status(std_scr, prompt + visible)

        try:
            key = std_scr.get_wch()
        except KeyboardInterrupt:
            return None

        if key in ("\n", "\r"):
            return "".join(characters)
        if key == "\x1b":
            return None
        if key in ("\b", "\x7f", curses.KEY_BACKSPACE):
            if characters:
                characters.pop()
        elif isinstance(key, str) and key.isprintable():
            characters.append(key)
