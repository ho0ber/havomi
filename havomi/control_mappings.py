from collections import namedtuple
import yaml
import os
import havomi.windows_helpers as wh


MapEntry = namedtuple("MapEntry",["control", "channel"])

class ChannelMap(object):
    """
    The ChannelMap is the primary means by which we quickly look up incoming midi events
    to see if we "care" about them. This lookup needs to be very fast, otherwise we risk
    slowing down handling of important events downstream.
    """
    def __init__(self, channels):
        self.channels = {channel.cid:channel for channel in channels}
        self.cmap = {}
        self.build_map()

    def build_map(self):
        for channel in self.channels.values():
            for control in channel.dev_binding.controls:
                if control.type not in ["meter", "level"]:
                    self.cmap[f"{control.midi_type}:{control.midi_id}"] = MapEntry(control=control, channel=channel)

    def lookup(self, msg):
        if msg.type == "control_change":
            key = f"{msg.type}:{msg.control}"
            value = msg.value
        elif msg.type == "note_on":
            key = f"{msg.type}:{msg.note}"
            value = msg.velocity
        elif msg.type == "pitchwheel":
            key = f"{msg.type}:{msg.channel}"
            value = msg.pitch
        else:
            key = None
            value = None
        
        return self.cmap.get(key), value
    
    def last(self):
        return self.channels[max(self.channels.keys())]

    def file_path(self, filename):
        app_dir = os.path.join(os.getenv('LOCALAPPDATA'),"havomi")
        return os.path.join(app_dir, filename)

    def save(self):
        data = {
            "channels": {
                cid: [channel.target.name, channel.color] for cid,channel in self.channels
            }
        }

        with open(self.file_path("config.yaml"), "w") as config_file:
            yaml.dump(data, config_file)
    
    def load(self):
        app_sessions = wh.get_applications_and_sessions()
        with open(self.file_path("config.yaml")) as config_file:
            config = yaml.safe_load(config_file.read())
            for cid,chan_conf in config["channels"].items():
                name,color = chan_conf
                if name in app_sessions:
                    self.channels[cid].set_target_from_app_def(app_sessions)
                else:
                    self.channels[cid].set_target_from_app_def(wh.AppDef(name, color, []))

class SharedMap(object):
    def __init__(self, shared):
        self.smap = {}
        self.build_map(shared)

    def build_map(self, shared):
        for control in shared:
            if control.type not in ["meter", "level"]:
                self.smap[f"{control.midi_type}:{control.midi_id}"] = control

    def lookup(self, msg):
        if msg.type == "control_change":
            key = f"{msg.type}:{msg.control}"
            value = msg.value
        elif msg.type == "note_on":
            key = f"{msg.type}:{msg.note}"
            value = msg.velocity
        elif msg.type == "pitchwheel":
            key = f"{msg.type}:{msg.channel}"
            value = msg.pitch
        else:
            key = None
            value = None
        
        return self.smap.get(key), value
