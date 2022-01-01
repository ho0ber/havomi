from pprint import pprint
import mido
import mido.backends.rtmidi

from prompt_toolkit.shortcuts import radiolist_dialog

if __name__ == "__main__":
    inputs = mido.get_input_names()

    if not inputs:
        print("No inputs")
        exit()

    dev_name = radiolist_dialog(
        title="Select Device",
        text="Select a device to listen to",
        values=[(i,i) for i in inputs]
    ).run()

    while True:
        with mido.open_input(dev_name) as in_port:
            print(f"Listening on {dev_name}...")
            for msg in in_port:
                print(msg)
