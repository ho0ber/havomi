from dataclasses import dataclass
from dataclasses import dataclass, field
from collections import namedtuple
import mido
from scribble import scribble

MapEntry = namedtuple("MapEntry",["type", "channel"])

@dataclass
class Channel:
    cid: int
    name: str
    level: int
    color: str
    fid: int
    kid: int
    lid: int
    # todo:
    # dev_binding: DeviceChannel
    # target_binding: Target

    COLORS=["black","white","red","green","yellow","blue","cyan","magenta"]

    def update_scribble(self):
        return scribble(self.cid, color=self.color, top=self.name, bottom=self.level, inv_bot=True)

    def update_fader(self):
        return mido.Message("control_change",control=self.fid,value=self.level)

    def update_level(self):
        return mido.Message("control_change",control=self.lid,value=self.level)

    def change_color(self, inc):
        cur_index = self.COLORS.index(self.color)
        new_index = (cur_index+inc)%8
        self.color = self.COLORS[new_index]

# @dataclass
class ChannelMap(object):
    # cmap: field(default_factory=dict)
    # channels: field(default_factory=list)

    def __init__(self, channels):
        # self.channels = channels
        self.channels = {channel.cid:channel for channel in channels}
        self.cmap = {}
        self.build_map()

    def build_map(self):
        for channel in self.channels.values():
            self.cmap[f"control_change:{channel.fid}"] = MapEntry(type="fader", channel=channel)
            self.cmap[f"control_change:{channel.kid}"] = MapEntry(type="knob", channel=channel)

    def lookup(self, msg):
        match msg.type:
            case "control_change":
                key = f"{msg.type}:{msg.control}"
                value = msg.value
            case _:
                key = None
                value = None
        
        return self.cmap.get(key), value
