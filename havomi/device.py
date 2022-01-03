import yaml
import mido
import mido.backends.rtmidi
import time
from havomi.controls import *
from havomi.device_channel import DeviceChannel

class Device(object):
    """
    This class represents the midi device being used to control volumes. It is responsible for
    parsing config and providing a midi out port for sending feedback midi events to the device.
    """
    def __init__(self, dev_info):
        self.in_name = dev_info["input"]
        self.out_name = dev_info["output"]
        filename = dev_info["device"]
        with open(filename) as device_file:
            self.config = yaml.safe_load(device_file.read())
        self.name = self.config["display_name"]
        self.device_channels = self.build_channels()
        self.shared_controls = self.build_shared_controls()
        self.scribble = self.config.get("scribble", False)
        self.out_port = self.open_out_port()
        self.unique_id = self.config["unique_id"]

    def open_out_port(self):
        out_port = None
        while out_port is None:
            try:
                out_port = mido.open_output(self.out_name)
            except OSError as e:
                if self.out_name in str(e):
                    print(f"Couldn't connect to midi device to to send: {e}")
                    print("Retrying in 5 seconds")
                    time.sleep(5)
                else:
                    print(e)
                    break
        return out_port

    def build_shared_controls(self):
        shared_controls = []
        for con_conf in self.config.get("shared",[]):
            shared_controls.append(self.build_control(con_conf))
        return shared_controls

    def build_channels(self):
        channels = []
        for chan_config in self.config["channels"]:
            channel = DeviceChannel(cid=chan_config["cid"], default=chan_config.get("default"), controls=[])
            for con_conf in chan_config["controls"]:
                channel.controls.append(self.build_control(con_conf))
            channels.append(channel)
        return channels
    
    def build_control(self, conf):
        if conf["type"] == "fader":
            mtype = self.inflate(conf["mtype"])
            m_id_field,m_val_field = self.look_up_fields(mtype)
            return Fader(
                type=conf["type"],
                func=conf["func"],
                midi_type=mtype,
                midi_id_field=m_id_field,
                midi_id=conf["mid"],
                midi_value_field=m_val_field,
                feedback=conf["fb"],
                midi_value_min=conf["min"],
                midi_value_max=conf["max"]
            )
        elif conf["type"] == "knob":
            mtype = self.inflate(conf["mtype"])
            m_id_field,m_val_field = self.look_up_fields(mtype)
            return RotaryEncoder(
                type=conf["type"],
                func=conf["func"],
                midi_type=mtype,
                midi_id_field=m_id_field,
                midi_id=conf["mid"],
                midi_value_field=m_val_field,
                feedback=conf["fb"],
                increment_value=conf["inc"],
                decrement_value=conf["dec"],
                accel=conf.get("accel", False),
            )
        elif conf["type"] == "button":
            mtype = self.inflate(conf["mtype"])
            m_id_field,m_val_field = self.look_up_fields(mtype)
            return Button(
                type=conf["type"],
                func=conf["func"],
                midi_type=mtype,
                midi_id_field=m_id_field,
                midi_id=conf["mid"],
                midi_value_field=m_val_field,
                feedback=conf["fb"],
            )
        elif conf["type"] == "meter":
            mtype = self.inflate(conf["mtype"])
            m_id_field,m_val_field = self.look_up_fields(mtype)
            return Meter(
                type=conf["type"],
                func=conf["func"],
                midi_type=mtype,
                midi_id_field=m_id_field,
                midi_id=conf["mid"],
                midi_value_field=m_val_field,
                feedback=conf["fb"],
                min=conf.get("min", 0),
                max=conf.get("max", 127),
                unset=conf.get("unset", 0)
            )

    def inflate(self, event_type):
        if event_type == "pw":
            return "pitchwheel"
        elif event_type == "note":
            return "note_on"
        elif event_type == "cc":
            return "control_change"
        else:
            return event_type

    def look_up_fields(self, mtype):
        if mtype ==  "control_change":
            return "control","value"
        elif mtype == "note_on":
            return "note","velocity"
        elif mtype == "pitchwheel":
            return "channel","pitch"
