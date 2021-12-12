from dataclasses import dataclass
from collections import namedtuple
import mido
from device import DeviceChannel
from target import Target
from scribble import scribble

MapEntry = namedtuple("MapEntry",["type", "channel"])

@dataclass
class Channel:
    cid: int
    name: str
    level: int
    color: str
    dev_binding: DeviceChannel
    target: Target

    def update_scribble(self):
        return scribble(self.cid, color=self.color, top=self.name, bottom=self.level, inv_bot=True)

    def update_fader(self):
        d = self.dev_binding
        c = d.find_control("fader")
        if c.feedback:
            kwargs = {
                c.midi_id_field: c.midi_id,
                c.midi_value_field: self.level
            }
            return mido.Message(c.midi_type,**kwargs)

    def update_level(self):
        d = self.dev_binding
        c = d.find_control("level")
        if c.feedback:
            kwargs = {
                c.midi_id_field: c.midi_id,
                c.midi_value_field: self.level
            }
            return mido.Message(c.midi_type,**kwargs)

    def change_color(self, inc):
        colors = ["black","white","red","green","yellow","blue","cyan","magenta"]
        cur_index = colors.index(self.color)
        new_index = (cur_index+inc)%8
        self.color = colors[new_index]

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
            for control in channel.dev_binding.controls:
                self.cmap[f"{control.midi_type}:{control.midi_id}"] = MapEntry(type=control.type, channel=channel)

    def lookup(self, msg):
        match msg.type:
            case "control_change":
                key = f"{msg.type}:{msg.control}"
                value = msg.value
            case "note_on":
                key = f"{msg.type}:{msg.note}"
                value = msg.velocity
            case _:
                key = None
                value = None
        
        return self.cmap.get(key), value
