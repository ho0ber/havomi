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
    def __init__(self, channels, device_id):
        self.channels = {channel.cid:channel for channel in channels}
        self.cmap = {}
        self.device_id = device_id
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
        # app_dir = os.path.join(os.getenv('LOCALAPPDATA'),"havomi")
        abs_home = os.path.abspath(os.path.expanduser("~"))
        app_dir = os.path.join(abs_home, ".havomi")
        device_dir = os.path.join(app_dir, self.device_id)
        if not os.path.exists(device_dir):
            print(f"Directory {device_dir} doesn't exist; creating.")
            os.mkdir(device_dir)
        return os.path.join(device_dir, filename)

    def save(self):
        data = {
            "channels": {
                cid: [channel.target.name, channel.color] for cid,channel in self.channels.items() if channel is not None and channel.target is not None
            }
        }

        with open(self.file_path("config.yaml"), "w") as config_file:
            yaml.dump(data, config_file)
    
    def load(self):
        filename = self.file_path("config.yaml")
        if os.path.exists(filename):
            print(f"Found config file: {filename}")
            with open(filename) as config_file:
                raw_config = config_file.read()
                print(raw_config)
                config = yaml.safe_load(raw_config)
            for cid,chan_conf in config["channels"].items():
                name,color = chan_conf
                self.channels[cid].set_target_from_app_def(wh.AppDef(name, color, []))
            return True
        else:
            print(f"No config file found at {filename}; skipping load.")
            return False

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
