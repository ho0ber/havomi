import multiprocessing
import pathlib

import havomi.midi_listener as midi_listener
import havomi.system_listener as system_listener
import havomi.event_handler as event_handler
from havomi.device import Device
from havomi.channel import Channel
from havomi.control_mappings import ChannelMap, SharedMap
from havomi.interface import get_config

DIR = pathlib.Path(__file__).parent.parent.resolve()
DEVICES = DIR.joinpath("devices")
if not DEVICES.is_dir():
    DIR = pathlib.Path(__file__).parent.resolve()
    DEVICES = DIR.joinpath("devices")

def init_channels(dev):
    """
    Initialize the Channels with basic mappings to the DeviceChannels. This will also configure
    any DeviceChannels where default==master.
    """
    shared_map = SharedMap(dev.shared_controls)
    channel_map = ChannelMap([
        Channel(
            cid=i,
            name="Unused",
            color="black",
            level=0,
            mute=False,
            dev_binding=dev.device_channels[i],
            target=None
        )
        for i in range(len(dev.device_channels))
    ], dev.unique_id)

    for channel in channel_map.channels.values():
        if channel.dev_binding.default == "master":
            channel.set_master()
        channel.update_display(dev, fader=True)

    return shared_map, channel_map

def start():
    """
    This is the primary entry point for the application. We're running multiprocessing here so we
    can have totally separate processes listening for midi events and system events, all funneling
    into a single event queue to be processed by the event_handler. Listeners are intended to be
    "dumb" and not do significant processing in their processes, saving most filtering and
    processing for the handler.
    """
    multiprocessing.freeze_support()

    dev_info = get_config()
    dev = Device(dev_info)
    shared_map, channel_map = init_channels(dev)
    event_queue = multiprocessing.Queue()

    midi_listener_process = multiprocessing.Process(target = midi_listener.start, args=(event_queue,dev.in_name))
    system_listener_process = multiprocessing.Process(target = system_listener.start, args=(event_queue,))

    midi_listener_process.start()
    system_listener_process.start()

    try:
        event_handler.start(event_queue, dev, shared_map, channel_map)
    except Exception as e:
        raise e
    finally:
        print("Shutting down listener processes")
        midi_listener_process.terminate()
        system_listener_process.terminate()
