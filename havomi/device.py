from collections import defaultdict
import yaml
import mido

class Device(object):
    def __init__(self, filename):
        with open(filename) as device_file:
            self.config = yaml.safe_load(device_file.read())
        self.input_map = self._build_input_map()

        self.in_port = mido.open_input(self.config["device_names"]["input"])
        self.out_port = mido.open_output(self.config["device_names"]["output"])
        self.name = self.config["display_name"]
        self.event_queue = defaultdict(list)
    
    def _build_input_map(self):
        input_map = {}
        for cg in self.config["control_groups"]:
            for i,control in enumerate(cg["controls"]):
                for element,e_config in control.items():
                    input_map[self._build_key(e_config)] = {
                        "index":i,
                        "element":element,
                        "config":e_config,
                        "control":control,
                    }
        return input_map

    def _build_key(self, e_config: dict):
        match e_config["type"]:
            case "cc":
                return f"cc:{e_config['control']}"
            case "note":
                return f"note:{e_config['note']}"
            case "pw":
                return f"pw:{e_config['channel']}"

    def _build_key_from_event(self, msg):
        match msg.type:
            case "control_change":
                return f"cc:{msg.control}"
            case "note_on":
                return f"note:{msg.note}"
            case "pitchwheel":
                return f"pw:{msg.channel}"

    def get_value(self, msg, found):
        conf = found["config"]
        match conf["field"]:
            case "value":
                if "dec" in conf and msg.value == conf["dec"]:
                    return "-"
                if "inc" in conf and msg.value == conf["inc"]:
                    return "+"
                return msg.value
            case "velocity":
                return msg.velocity
            case "pitch":
                return msg.pitch

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

    def match_input(self, msg):
        key = self._build_key_from_event(msg)
        if found:= self.input_map.get(key):
            conf = found["config"]
            val = self.get_value(msg, found)
            print(f"{found['element']} {found['index']} got an event: {val}")
            if conf.get("feedback") == "confirm":
                kwargs = {k:conf[k] for k in ["channel","note","control"] if k in conf}
                kwargs[conf["field"]] = min((val),conf.get("max"))
                self.event_queue[found["index"]].append(mido.Message(self.inflate(conf["type"]), **kwargs))
            if conf.get("lock") and val == 0:
                out_msg = self.event_queue[found["index"]].pop()
                print(f"Sending: {out_msg}")
                self.out_port.send(out_msg)
                del self.event_queue[found["index"]]

    def listen(self):
        # self.dance()
        print(f"Listening on {self.name}")
        for msg in self.in_port:
            # print(msg)
            self.match_input(msg)
