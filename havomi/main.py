import multiprocessing
import pathlib

# from device import Device
import midi_listener
import system_listener
import event_handler

DIR = pathlib.Path(__file__).parent.parent.resolve()
DEVICES = DIR.joinpath("devices")


if __name__ == "__main__":
    dev = Device(DEVICES.joinpath("xte.yaml"))
    # dev.listen()
    event_queue = multiprocessing.Queue()
    midi_listener_process = multiprocessing.Process(target = midi_listener.start, args=(event_queue,))
    system_listener_process = multiprocessing.Process(target = system_listener.start, args=(event_queue,))

    midi_listener_process.start()
    system_listener_process.start()
    event_handler.start(event_queue, dev)
    midi_listener_process.join()
    system_listener_process.join()
