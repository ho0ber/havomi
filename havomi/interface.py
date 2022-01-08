import yaml
import mido
import mido.backends.rtmidi
from infi.systray import SysTrayIcon
from os import listdir
from os.path import join, dirname, realpath, abspath, exists, expanduser

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

def match_dev(name, dev_list):
    if name is None:
        return None
    for dev in dev_list:
        if dev.startswith(name):
            return dev
    return None

def custom_device_files():
    abs_home = abspath(expanduser("~"))
    app_dir = join(abs_home, ".havomi")
    custom_dev = join(app_dir, "custom")
    if exists(custom_dev):
        print("Found custom files:")
        return [(f"custom:{x}",join(custom_dev, x)) for x in listdir(custom_dev) if x.endswith(".yaml")]
    else:
        print(f"{custom_dev} does not exist")
        return []

def find_connected_device(inputs, outputs):
    devices_path = join(dirname(dirname(realpath(__file__))),"devices")
    device_configs = [(x,join(devices_path, x)) for x in listdir(devices_path) if x.endswith(".yaml")]
    device_configs += custom_device_files()

    dev_matches = {}
    for config_filename,config_path in device_configs:
        with open(config_path) as config_file:
            config = yaml.safe_load(config_file.read())
        conf_input = config.get("device_names",{}).get("windows",{}).get("input")
        conf_output = config.get("device_names",{}).get("windows",{}).get("output")
        input_match = match_dev(conf_input, inputs)
        output_match = match_dev(conf_output, outputs)
        if input_match and output_match:
            dev_matches[config_filename] = [config_path, input_match, output_match]
    
    if len(dev_matches.keys()) > 1:
        chosen_device = chooser("Multiple devices detected; select one:", list(dev_matches.keys()))
        path, input_dev, output_dev = dev_matches[chosen_device]
    elif len(dev_matches.keys()) == 0:
        chosen_device = chooser("No devices detected; select a config:", device_configs)
        path = join(devices_path, chosen_device)
        input_dev = chooser("Choose your input device", inputs)
        output_dev = chooser("Choose your input device", outputs)
    else:
        chosen_device = list(dev_matches.keys())[0]
        path, input_dev, output_dev = dev_matches[chosen_device]
    
    return path, input_dev, output_dev

def get_config():
    """
    Prompts the user on the command-line for a device config file and, if necessary, input and
    output devices if the entries in the device config file don't match any connected midi devices.
    """
    inputs = mido.get_input_names()
    outputs = mido.get_output_names()

    device_filename, input_dev, output_dev = find_connected_device(inputs, outputs)

    return {
        "input": input_dev,
        "output": output_dev,
        "device": device_filename,
    }

def systray(event_queue):

    def say_hello(systray):
        print("Hello, World!")
    
    def quit(systray):
        event_queue.put(("interface", {"action": "quit"}))

    def assign(systray):
        
        event_queue.put(("interface", {"action": "quit"}))
    
    def change_color(systray):
        event_queue.put(("interface", {"action": "quit"}))

    menu_options = (
        ("Say Hello", None, say_hello),
        ("Fader 1", None, (
            ("Assign", None, assign),
            ("Change color", None, change_color),
        ))
    )
    systray = SysTrayIcon("icon.ico", "Example tray icon", menu_options, on_quit=quit)
    systray.start()
    return systray
