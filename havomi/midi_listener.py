import multiprocessing
import mido
import mido.backends.rtmidi
import time

from havomi.device import Device

# def stop(dev, midi_listener_process):
#     dev.out_port.close()
#     midi_listener_process.terminate()

# def init(dev_info, event_queue):
#     dev = Device(dev_info)
#     shared_map, channel_map = dev.init_channels()
#     if channel_map.load():
#         for channel in channel_map.channels.values():
#             channel.update_display(dev, fader=True)
#     midi_listener_process = multiprocessing.Process(target = start, args=(event_queue, dev.in_name))

#     return shared_map, channel_map, dev, midi_listener_process

def start(event_queue, dev_name):
    """
    This is the entry point for the midi listener process. It simply listens for all midi events
    on the specified input device and sends them to the event handler via the event queue.
    """
    while True:
        try:
            with mido.open_input(dev_name) as in_port:
                print(f"Listening on {dev_name}...")
                for msg in in_port:
                    event_queue.put(("midi",msg))
        except OSError as e:
            if dev_name in str(e):
                print(f"Couldn't connect to midi device to listen:\n{e}")
                print("Retrying in 5 seconds")
                time.sleep(5)
            else:
                print(e)
                break
