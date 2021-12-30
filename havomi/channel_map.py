from collections import namedtuple

MapEntry = namedtuple("MapEntry",["type", "channel"])

class ChannelMap(object):
    def __init__(self, channels):
        self.channels = {channel.cid:channel for channel in channels}
        self.cmap = {}
        self.build_map()

    def build_map(self):
        for channel in self.channels.values():
            for control in channel.dev_binding.controls:
                self.cmap[f"{control.midi_type}:{control.midi_id}"] = MapEntry(type=control.type, channel=channel)

    def lookup(self, msg):
        if msg.type == "control_change":
            key = f"{msg.type}:{msg.control}"
            value = msg.value
        elif msg.type == "note_on":
            key = f"{msg.type}:{msg.note}"
            value = msg.velocity
        else:
            key = None
            value = None
        
        return self.cmap.get(key), value