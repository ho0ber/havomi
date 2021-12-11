import mido

def start(event_queue):
    dev = "X-Touch-Ext X-TOUCH_INT"
    with mido.open_input(dev) as in_port:
        print(f"Listening on {dev}...")
        for msg in in_port:
            event_queue.put(("midi",msg))
