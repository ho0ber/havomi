import platform
import yaml
import mido
import mido.backends.rtmidi
from os import listdir
from os.path import join, dirname, realpath
from prompt_toolkit.shortcuts import radiolist_dialog, input_dialog

def get_device_file():
    """
    Asks the user for a device config yaml. It offers a list from the devices directory built-in,
    but also allows for a user to input a path manually.
    """
    devices_path = join(dirname(dirname(realpath(__file__))),"devices")
    devices = [x for x in listdir(devices_path) if x.endswith(".yaml")]
    dev_name = radiolist_dialog(
        title="Select Config",
        text="Select a device config",
        values=[(join(devices_path, d),d) for d in devices]+[("custom","Custom")]
    ).run()

    if dev_name == "custom":
        dev_name = input_dialog(
            title='Custom config',
            text='Path to device config:').run()

    print(dev_name)
    return dev_name

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
        input_dev = radiolist_dialog(
            title="Select Device",
            text="Choose your input device",
            values=[(i,i) for i in inputs]
        ).run()

    if output_dev is None:
        output_dev = radiolist_dialog(
            title="Select Device",
            text="Choose your output device",
            values=[(o,o) for o in outputs]
        ).run()

    return {
        "input": input_dev,
        "output": output_dev,
        "device": device_filename,
    }
