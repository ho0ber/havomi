import multiprocessing
import pathlib

import havomi.midi_listener as midi_listener
import havomi.system_listener as system_listener
import havomi.event_handler as event_handler
from havomi.device import Device
from havomi.interface import get_config, systray

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
    
    try:
        while True:
            event_queue = multiprocessing.Queue()
            update_queue = multiprocessing.Queue()

            # shared_map, channel_map, dev, midi_listener_process = midi_listener.init(dev_info, event_queue)
            dev = Device(dev_info)
            shared_map, channel_map = dev.init_channels()
            if channel_map.load():
                for channel in channel_map.channels.values():
                    channel.update_display(dev, fader=True)

            midi_listener_process = multiprocessing.Process(target = midi_listener.start, args=(event_queue, dev.in_name))
            system_listener_process = multiprocessing.Process(target = system_listener.start, args=(event_queue,))
            systray_priocess = multiprocessing.Process(target = systray, args=(event_queue, update_queue, len(channel_map.channels.keys()), dev_info))

            system_listener_process.start()
            systray_priocess.start()
            midi_listener_process.start()
            print("Got past process starts...")

            exit_status, exit_data = event_handler.start(event_queue, dev, shared_map, channel_map, update_queue)

            if exit_status == "quit":
                break
            if exit_status == "restart_midi":
                print("Restarting")
                dev.out_port.close()
                system_listener_process.terminate()
                systray_priocess.terminate()
                midi_listener_process.terminate()
                system_listener_process.join()
                systray_priocess.join()
                midi_listener_process.join()
                dev_info = exit_data

    except Exception as e:
        print(f"Exception? {e}")
        raise e
    finally:
        print("Shutting down listener processes")
        system_listener_process.terminate()
        systray_priocess.terminate()
        midi_listener_process.terminate()
