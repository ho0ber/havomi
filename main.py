import multiprocessing
import pathlib

import havomi.midi_listener as midi_listener
import havomi.system_listener as system_listener
import havomi.event_handler as event_handler
from havomi.device import Device
from havomi.channel import Channel
from havomi.channel_map import ChannelMap
from havomi.target import Target
from pycaw.pycaw import AudioUtilities

DIR = pathlib.Path(__file__).parent.parent.resolve()
DEVICES = DIR.joinpath("devices")
if not DEVICES.is_dir():
    DIR = pathlib.Path(__file__).parent.resolve()
    DEVICES = DIR.joinpath("devices")

def init_channels(dev):
    
    channel_map = ChannelMap([
        Channel(cid=0, name="Unused", color="black",   level=0, dev_binding=dev.device_channels[0], target=None),
        Channel(cid=1, name="Unused", color="black",     level=0, dev_binding=dev.device_channels[1], target=None),
        Channel(cid=2, name="Unused", color="black",    level=0, dev_binding=dev.device_channels[2], target=None),
        Channel(cid=3, name="Unused", color="black",  level=0, dev_binding=dev.device_channels[3], target=None),
        Channel(cid=4, name="Unused", color="black",    level=0, dev_binding=dev.device_channels[4], target=None),
        Channel(cid=5, name="Unused", color="black", level=0, dev_binding=dev.device_channels[5], target=None),
        Channel(cid=6, name="Unused", color="black",   level=0, dev_binding=dev.device_channels[6], target=None),
        Channel(cid=7, name="Master", color="white",   level=0, dev_binding=dev.device_channels[7], target=None),
    ])

    # sessions = AudioUtilities.GetAllSessions()
    # for i,session in enumerate(sessions):
    #     channel = channel_map.channels[i]
    #     channel.name = session.Process.name() if session.Process else "None"
    #     channel.target = Target(channel.name, "application", session)
    #     channel.get_level_from_target()

    for channel in channel_map.channels.values():
        dev.out_port.send(channel.update_scribble())
        dev.out_port.send(channel.update_level())
        dev.out_port.send(channel.update_fader())

    return channel_map

if __name__ == "__main__":
    multiprocessing.freeze_support()
    dev = Device(DEVICES.joinpath("xte.yaml"))
    channel_map = init_channels(dev)
    # dev.listen()
    event_queue = multiprocessing.Queue()
    midi_listener_process = multiprocessing.Process(target = midi_listener.start, args=(event_queue,dev.in_name))
    system_listener_process = multiprocessing.Process(target = system_listener.start, args=(event_queue,))

    midi_listener_process.start()
    system_listener_process.start()
    event_handler.start(event_queue, dev, channel_map)
    midi_listener_process.join()
    system_listener_process.join()
