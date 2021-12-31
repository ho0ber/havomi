import multiprocessing
import pathlib

import havomi.midi_listener as midi_listener
import havomi.system_listener as system_listener
import havomi.event_handler as event_handler
from havomi.device import Device
from havomi.channel import Channel
from havomi.channel_map import ChannelMap
from havomi.target import Target
from havomi.interface import get_config

DIR = pathlib.Path(__file__).parent.parent.resolve()
DEVICES = DIR.joinpath("devices")
if not DEVICES.is_dir():
    DIR = pathlib.Path(__file__).parent.resolve()
    DEVICES = DIR.joinpath("devices")

def init_channels(dev):
    
    channel_map = ChannelMap([
        Channel(
            cid=i,
            name="Unused",
            color="black",
            level=0,
            dev_binding=dev.device_channels[i],
            target=None
        )
        for i in range(len(dev.device_channels))
    ])
    channel_map.last().set_master()

    for channel in channel_map.channels.values():
        dev.out_port.send(channel.update_scribble())
        dev.out_port.send(channel.update_level())
        dev.out_port.send(channel.update_fader())

    return channel_map

def start():
    multiprocessing.freeze_support()
    dev_info = get_config()
    dev = Device(dev_info)
    channel_map = init_channels(dev)
    event_queue = multiprocessing.Queue()
    midi_listener_process = multiprocessing.Process(target = midi_listener.start, args=(event_queue,dev.in_name))
    system_listener_process = multiprocessing.Process(target = system_listener.start, args=(event_queue,))

    midi_listener_process.start()
    system_listener_process.start()
    event_handler.start(event_queue, dev, channel_map)
    midi_listener_process.terminate()
    system_listener_process.terminate()

