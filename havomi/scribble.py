import mido

def lookup_color(color, inv_top, inv_bot):
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
