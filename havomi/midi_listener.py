import mido
import mido.backends.rtmidi
import time

def start(event_queue, dev_name):
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
