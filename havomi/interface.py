import platform
import yaml
import mido
import mido.backends.rtmidi
from os import listdir
from os.path import join, dirname, realpath

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

def get_device_file():
    """
    Asks the user for a device config yaml. It offers a list from the devices directory built-in,
    but also allows for a user to input a path manually.
    """
    devices_path = join(dirname(dirname(realpath(__file__))),"devices")
    devices = [x for x in listdir(devices_path) if x.endswith(".yaml")]
    dev_name = chooser("Select a device config", devices)
    return join(devices_path, dev_name)

def match_dev(name, dev_list):
    if name is None:
        return None
    for dev in dev_list:
        if dev.startswith(name):
            return dev
    return None

def get_config():
    """
    Prompts the user on the command-line for a device config file and, if necessary, input and
    output devices if the entries in the device config file don't match any connected midi devices.
    """
    device_filename = get_device_file()
    os = platform.system()

    inputs = mido.get_input_names()
    outputs = mido.get_output_names()

    with open(device_filename) as device_file:
        config = yaml.safe_load(device_file.read())

    if os.lower() == "windows":
        conf_input = config.get("device_names",{}).get("windows",{}).get("input")
        conf_output = config.get("device_names",{}).get("windows",{}).get("output")
    
    input_dev = match_dev(conf_input, inputs)
    output_dev = match_dev(conf_output, outputs)

    if input_dev is None:
        input_dev = chooser("Choose your input device", inputs)

    if output_dev is None:
        output_dev = chooser("Choose your input device", outputs)

    return {
        "input": input_dev,
        "output": output_dev,
        "device": device_filename,
    }
