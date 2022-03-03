import yaml
import mido
import mido.backends.rtmidi
from havomi.windows_helpers import get_application_names
from PIL import Image, ImageDraw
from pystray import Icon, Menu, MenuItem
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

def static_path():
    return join(dirname(dirname(realpath(__file__))), "static")

def custom_device_files():
    abs_home = abspath(expanduser("~"))
    app_dir = join(abs_home, ".havomi")
    custom_dev = join(app_dir, "custom")
    if exists(custom_dev):
        return [(f"custom:{x}",join(custom_dev, x)) for x in listdir(custom_dev) if x.endswith(".yaml")]
    else:
        print(f"{custom_dev} does not exist")
        return []

def find_connected_device(inputs, outputs):
    devices_path = join(static_path(),"devices")
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

def load_icon():
    im = Image.open(join(static_path(), "images", "tray_16.png"))
    im = im.convert('RGBA')
    return im

def create_image():
    # Generate an image and draw a pattern
    width = 64
    height = 64
    color1 = "red"
    color2 = "black"
    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle(
        (width // 2, 0, width, height // 2),
        fill=color2)
    dc.rectangle(
        (0, height // 2, width // 2, height),
        fill=color2)

    return image

class AppMenuItemAction(object):
    def __init__(self, app_name, cid, app_state):
        self.app_name = app_name
        self.cid = cid
        self.app_state = app_state
    
    def __call__(self, arg1=None, arg2=None, arg3=None):
        self.app_state.event_queue.put(("interface", {"action": "assign", "app": self.app_name, "channel": self.cid}))

class AppMenu(object):
    def __init__(self, cid, app_state):
        self.cid = cid
        self.app_state = app_state
    
    def __call__(self, arg1=None, arg2=None, arg3=None):
        applications = get_application_names()
        menu = []
        for an in applications:
            menu.append(MenuItem(an, AppMenuItemAction(an, self.cid, self.app_state)))
        return menu

class AssignMenuItem(object):
    def __init__(self, cid, app_state):
        self.cid = cid
        self.app_state = app_state

    def __call__(self, arg1=None, arg2=None, arg3=None):
        return f"Assign Fader {self.cid}"

class FaderMenuItem(object):
    def __init__(self, cid, app_state):
        self.cid = cid
        self.app_state = app_state

    def __call__(self, arg1=None, arg2=None, arg3=None):
        if self.app_state.channels[self.cid]["assigned"]:
            app_name = self.app_state.channels[self.cid]["name"]
            return f"Fader {self.cid}: {app_name}"
        else:
            return f"Fader {self.cid}"

class UnassignAction(object):
    def __init__(self, cid, app_state):
        self.cid = cid
        self.app_state = app_state

    def __call__(self, arg1=None, arg2=None, arg3=None):
        self.app_state.event_queue.put(("interface", {"action": "unassign", "channel": self.cid}))

class InputDeviceMenu(object):
    def __init__(self, app_state):
        self.app_state = app_state
    
    def __call__(self, arg1=None, arg2=None, arg3=None):
        inputs = mido.get_input_names()
        menu = []
        for input in inputs:
            checked = (self.app_state.dev_info.get("input") == input)
            menu.append(MenuItem(input, Menu(OutputDeviceMenu(input, self.app_state))))
        return menu

class OutputDeviceMenu(object):
    def __init__(self, input, app_state):
        self.input = input
        self.app_state = app_state
    
    def __call__(self, arg1=None, arg2=None, arg3=None):
        outputs = mido.get_output_names()
        menu = []
        for output in outputs:
            checked = (self.app_state.dev_info.get("output") == output)
            menu.append(MenuItem(output, Menu(DeviceFileMenu(self.input, output, self.app_state))))
        return menu

class DeviceFileMenu(object):
    def __init__(self, input, output, app_state):
        self.input = input
        self.output = output
        self.app_state = app_state
    
    def __call__(self, arg1=None, arg2=None, arg3=None):
        devices_path = join(static_path(),"devices")
        device_configs = [(x,join(devices_path, x)) for x in listdir(devices_path) if x.endswith(".yaml")]
        device_configs += custom_device_files()

        menu = []
        for choice in self.app_state.find_dev_files(self.input, self.output):
            menu.append(MenuItem(choice[0], DeviceFileMenuItemAction(self.input, self.output, choice, self.app_state)))
        return menu

class DeviceFileMenuItemAction(object):
    def __init__(self, input, output, dev_file_info, app_state):
        self.input = input
        self.output = output
        self.app_state = app_state
        self.dev_file_info = dev_file_info
        self.dev_filename, self.dev_file_path = self.dev_file_info
    
    def __call__(self, arg1=None, arg2=None, arg3=None):
        self.app_state.event_queue.put(("interface", {"action": "change_dev", "dev_info": {"input": self.input, "output": self.output, "device": self.dev_file_path}}))


class MenuItems(object):
    def __init__(self, app_state):
        self.app_state = app_state

    def __call__(self, arg1=None, arg2=None, arg3=None):
        mi = []
        for i in range(self.app_state.num_channels):
            mi.append(
                MenuItem(
                    FaderMenuItem(i, self.app_state),
                    Menu(
                        MenuItem(AssignMenuItem(i, self.app_state), Menu(AppMenu(i, self.app_state))),
                        MenuItem("Unassign", UnassignAction(i, self.app_state)),
                    )
                )
            )
        mi.append(MenuItem("Midi Device", Menu(InputDeviceMenu(self.app_state))))
        mi.append(MenuItem("Quit", lambda : self.app_state.event_queue.put(("interface", {"action": "quit"}))))
        return mi

class AppState(object):
    def __init__(self, num_channels, event_queue, dev_info):
        self.num_channels = num_channels
        self.event_queue = event_queue
        self.application_names = get_application_names()
        self.in_devices = mido.get_input_names()
        self.out_devices = mido.get_output_names()
        self.dev_info = dev_info
        self.gen_channels()
        self.collect_dev_files()
    
    def collect_dev_files(self):
        devices_path = join(static_path(),"devices")
        device_configs = [(x,join(devices_path, x)) for x in listdir(devices_path) if x.endswith(".yaml")]
        device_configs += custom_device_files()

        dev_files = {}
        for config_filename,config_path in device_configs:
            with open(config_path) as config_file:
                config = yaml.safe_load(config_file.read())
                conf_input = config.get("device_names",{}).get("windows",{}).get("input")
                conf_output = config.get("device_names",{}).get("windows",{}).get("output")
                dev_files[(conf_input, conf_output)] = (config_filename,config_path)

        self.dev_files = dev_files

    def find_dev_files(self, input, output):
        found = []
        for devs,files in self.dev_files.items():
            if input.startswith(devs[0]) and output.startswith(devs[1]):
                found.append(files)
        return found
    
    def gen_channels(self):
        self.channels = {}
        for i in range(self.num_channels):
            self.channels[i] = {
                "assigned": False,
                "name": None,
            }
    def update(self, state):
        apps = get_application_names()
        updated = any([
            state["num_channels"] != self.num_channels,
            state["channels"] != self.channels,
            apps != self.application_names,
        ])
        self.num_channels = state["num_channels"]
        self.channels = state["channels"]
        self.application_names = apps
        self.in_devices = mido.get_input_names()
        self.out_devices = mido.get_output_names()
        return updated

def systray(event_queue, update_queue, num_channels, dev_info):
    print("Starting systray...")
    app_state = AppState(num_channels, event_queue, dev_info)
    menu_options = Menu(MenuItems(app_state))

    st = Icon("Havomi", load_icon(), menu=menu_options,)
    st.run_detached()
    
    # Process update events
    while True:
        event_type, event = update_queue.get()
        if event_type == "state":
            if app_state.update(event):
                print("Updating systray menu")
                st.update_menu()
