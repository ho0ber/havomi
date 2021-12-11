import mido
import time

color_map = {
    "black": 0,
    "red": 1,
    "green": 2,
    "yellow": 3,
    "blue": 4,
    "magenta": 5,
    "cyan": 6,
    "white": 7,
}

def lookup_color(color, inv_top, inv_bot):
    offset = inv_top*16 + inv_bot*32
    match color.lower():
        case ("black" | "b"):
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

def scribble(channel, color="black", top="", bottom="", inv_top=False, inv_bot=False):
    # start = [0xF0]
    manuf = [0x00,0x20,0x32]
    dev_id = [0x15] #NOT 42 like it says in the manual
    unk = [0x4C]
    chan = [channel]
    backlight = [lookup_color(color, inv_top, inv_bot)] #[0x16]
    top_hex = [ord(char) for char in (top+"\0"*7)[:7]]
    bot_hex = [ord(char) for char in (bottom+"\0"*7)[:7]]
    # end = [0xF7]

    return manuf+dev_id+unk+chan+backlight+top_hex+bot_hex

def msg(data):
    return mido.Message("sysex", data=data)

# out_port.send(msg(scribble(0, "hello", "world", color="red", invert_top=True, invert_bottom=False)))

dev = "X-Touch-Ext X-TOUCH_INT"
with mido.open_output(dev) as out_port:

    import pdb; pdb.set_trace()
    # for i in range(8):
        # dat = [0,0x20,0x32,0x42,i,0x4c,0b0100000,97,97,97,97,97,97,97,97,97,97,97,97,97,97]
    # dat = [0x00, 0x00, 0x66, 0x58, 0x20, 0x41, 0x43, 0x68, 0x20, 0x31, 0x00, 0x00, 0x00, 0x20, 0x20, 0x20, 0x20, 0x61, 0x42, 0x33]
    # dat = [0x00,0x00,0x66,0x00,0x12,0x00,0x4C,0x35,0x30,0x52,0x35,0x30,0x20]
    datstr = "F0 00 20 32 15 4C 03 16 68 65 6c 6c 6f 00 00 77 6f 72 6c 64 00 00 F7"
    dat = [int(f"0x{s}", 16) for s in datstr.split()][1:-1]
    # dat = [0x00,0x00,0x66,0x58,0x20,0x41,0x43,0x68,0x20,0x31,0x00,0x00,0x00,0x61,0x62,0x63,0x64,0x65,0x66,0x67]
    msg = mido.Message('sysex', data=dat)
    print(msg.hex())
    out_port.send(msg)
    # time.sleep(0.1)

    

    for i in list(range(127))+list(reversed(range(127))):
    #     print(i)
        # CTRL REL mode
        out_port.send(mido.Message("control_change",control=90,value=i))
    #     # MC Mode
    #     out_port.send(mido.Message("aftertouch", channel=0, value=i))
        time.sleep(0.01)