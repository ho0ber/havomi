import mido
import mido.backends.rtmidi

def lookup_color(color, inv_top, inv_bot):
    """
    This maps a color name or appreviation and inversion flags to a color code to use in a sysex
    message to be sent to the X-Touch Extender or or other compatible scribble strips.
    """
    offset = inv_top*16 + inv_bot*32
    if color.lower() == "black":
        return 0 + offset
    elif color.lower() in ("red", "r"):
        return 1 + offset
    elif color.lower() in ("green", "g"):
        return 2 + offset
    elif color.lower() in ("yellow", "y"):
        return 3 + offset
    elif color.lower() in ("blue", "b"):
        return 4 + offset
    elif color.lower() in ("magenta", "m"):
        return 5 + offset
    elif color.lower() in ("cyan", "c"):
        return 6 + offset
    elif color.lower() in ("white", "w"):
        return 7 + offset
    else:
        return 0 + offset

def scribble(channel, color="black", top="", bottom="", inv_top=False, inv_bot=False, msg=True):
    """
    This contstructs a sysex midi message to update a given scribble strip.
    channel: integer channel ID to update
    color:   color string - see lookup_color
    top:     text to display on top half of scribble - 7 character limit
    bottom:  text to display on bottom half of scribble - 7 character limit
    inv_top: flag to invert the colors on the top of the scribble
    inv_bot: flag to invert the colors on the bottom of the scribble
    msg:     flag to return as a mido.Message, rather than as a list of hex codes
    """
    # start = [0xF0]
    manuf = [0x00,0x20,0x32]
    dev_id = [0x15] #NOT 42 like it says in the manual
    unk = [0x4C]
    chan = [channel]
    backlight = [lookup_color(color, inv_top, inv_bot)] #[0x16]
    top_hex = [ord(char) for char in (str(top)+"\0"*7)[:7]]
    bot_hex = [ord(char) for char in (str(bottom)+"\0"*7)[:7]]
    # end = [0xF7]

    data = manuf+dev_id+unk+chan+backlight+top_hex+bot_hex
    return mido.Message("sysex", data=data) if msg else data
