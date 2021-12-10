from device import Device
import pathlib

DIR = pathlib.Path(__file__).parent.parent.resolve()
DEVICES = DIR.joinpath("devices")


if __name__ == "__main__":
    dev = Device(DEVICES.joinpath("xte.yaml"))