import mido
import mido.backends.rtmidi

def chooser(prompt, choices):
    print(prompt)
    for i,choice in enumerate(choices):
        print(f"{i}) {choice}")
    
    while True:
        try:
            selection = int(input(":"))
        except ValueError or TypeError as e:
            pass
        else:
            if 0 <= selection < len(choices):
                return choices[selection]
        print("Bad input, try again.")

if __name__ == "__main__":
    inputs = mido.get_input_names()

    if not inputs:
        print("No inputs")
        exit()

    dev_name = chooser("Select a device to listen to", inputs)

    while True:
        with mido.open_input(dev_name) as in_port:
            print(f"Listening on {dev_name}...")
            for msg in in_port:
                print(msg)
