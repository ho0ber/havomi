import yaml
import mido

class Device(object):
    def __init__(self, filename):
        with open(filename) as device_file:
            self.config = yaml.safe_load(device_file.read())

        self.in_port = mido.open_input(self.config["device_names"]["input"])
        self.out_port = mido.open_input(self.config["device_names"]["input"])

    def listen(self):
        for msg in inport:
            print(msg)
