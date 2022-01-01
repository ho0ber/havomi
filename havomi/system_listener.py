import time
import random

def start(event_queue):
    """
    This is the entry point for the system listener process. It listens to system events such as
    volume changes and sends events to the event_queue to update motorized faders and other
    feedback controls on the device.
    """
    while True:
        time.sleep(0.5)
        
        # time.sleep(random.randint(5,15))
        # event = {"channel":random.randint(0,7), "level":random.randint(0,127)}
        # event_queue.put(("system", event))
