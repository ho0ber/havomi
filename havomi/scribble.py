import mido

def lookup_color(color, inv_top, inv_bot):
    offset = inv_top*16 + inv_bot*32
    match color.lower():
        case ("black"):
            return 0 + offset
        case ("red" | "r"):
            return 1 + offset
        case ("green" | "g"):
            return 2 + offset
        case ("yellow" | "y"):
            return 3 + offset
        case ("blue" | "b"):
            return 4 + offset
        case ("magenta" | "m"):
            return 5 + offset
        case ("cyan" | "c"):
            return 6 + offset
        case ("white" | "w"):
            return 7 + offset
        case _:
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
