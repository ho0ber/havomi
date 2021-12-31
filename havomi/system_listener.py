import time
import random

def start(event_queue):
    while True:
        time.sleep(0.5)
        
        # time.sleep(random.randint(5,15))
        # event = {"channel":random.randint(0,7), "level":random.randint(0,127)}
        # event_queue.put(("system", event))
