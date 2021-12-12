import yaml
import mido
from controls import *
from device_channel import DeviceChannel

class Device(object):
    def __init__(self, filename):
        with open(filename) as device_file:
            self.config = yaml.safe_load(device_file.read())
        self.name = self.config["display_name"]
        self.device_channels = self.build_channels()
        # self.in_port = mido.open_input(self.config["device_names"]["input"])
        self.out_port = mido.open_output(self.config["device_names"]["output"])

    def build_channels(self):
        channels = []
        for g in self.config["groups"]:
            for chan_config in g["channels"]:
                channel = DeviceChannel(cid=chan_config["cid"], controls=[])
                for con_conf in chan_config["controls"]:
                    channel.controls.append(self.build_control(con_conf))
                channels.append(channel)
        return channels
    
    def build_control(self, conf):
        match conf["type"]:
            case "fader":
                mtype = self.inflate(conf["mtype"])
                m_id_field,m_val_field = self.look_up_fields(mtype)
                return Fader(
                    type=conf["type"],
                    label=conf["label"],
                    midi_type=mtype,
                    midi_id_field=m_id_field,
                    midi_id=conf["mid"],
                    midi_value_field=m_val_field,
                    feedback=conf["fb"],
                    midi_value_min=conf["min"],
                    midi_value_max=conf["max"]
                )
            case "knob":
                mtype = self.inflate(conf["mtype"])
                m_id_field,m_val_field = self.look_up_fields(mtype)
                return RotaryEncoder(
                    type=conf["type"],
                    label=conf["label"],
                    midi_type=mtype,
                    midi_id_field=m_id_field,
                    midi_id=conf["mid"],
                    midi_value_field=m_val_field,
                    feedback=conf["fb"],
                    increment_value=conf["inc"],
                    decrement_value=conf["dec"]
                )
            case "button":
                mtype = self.inflate(conf["mtype"])
                m_id_field,m_val_field = self.look_up_fields(mtype)
                return Button(
                    type=conf["type"],
                    label=conf["label"],
                    midi_type=mtype,
                    midi_id_field=m_id_field,
                    midi_id=conf["mid"],
                    midi_value_field=m_val_field,
                    feedback=conf["fb"],
                )
            case "meter":
                mtype = self.inflate(conf["mtype"])
                m_id_field,m_val_field = self.look_up_fields(mtype)
                return Meter(
                    type=conf["mtype"],
                    label=conf["label"],
                    midi_type=mtype,
                    midi_id_field=m_id_field,
                    midi_id=conf["mid"],
                    midi_value_field=m_val_field,
                    feedback=conf["fb"],
                )

    def inflate(self, event_type):
        match event_type:
            case "pw":
                return "pitchwheel"
            case "note":
                return "note_on"
            case "cc":
                return "control_change"
            case _:
                return event_type

    def look_up_fields(self, mtype):
        match mtype:
            case "control_change":
                return "control","value"
            case "note_on":
                return "note","velocity"
            case "pitchwheel":
                return "channel","pitch"
