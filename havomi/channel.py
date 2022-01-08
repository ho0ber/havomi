import mido
import mido.backends.rtmidi
from dataclasses import dataclass

from havomi.device import DeviceChannel
from havomi.target import ApplicationVolume, DeviceVolume, SystemSoundsVolume, Target
from havomi.scribble import scribble
import havomi.windows_helpers as wh

@dataclass
class Channel:
    """
    The Channel is the virtual object that binds a DeviceChannel to a Target. Channels and
    DeviceChannels are distinct because we want a stored channel config to be portable betwween
    devices.

    cid:         Channel ID
    name:        Display name
    level:       Current volume level, 0-127
    color:       RGB+CYM+White+Black
    dev_binding: Channel in the device config
    target:      Target application or device
    """
    cid: int
    name: str 
    level: int
    mute: bool
    color: str
    dev_binding: DeviceChannel
    target: Target
    touch_lock: bool = False

    def update_display(self, dev, fader=False):
        self.update_scribble(dev)
        self.update_level(dev)
        self.update_meter(dev)
        self.update_select(dev)
        self.update_mute(dev)
        if fader:
            self.update_fader(dev)

    def update_mute(self, dev):
        c = self.dev_binding.find_control("mute")
        if c and c.feedback:
            if self.target:
                value = c.down_value if self.mute else c.up_value
            else:
                value = c.up_value

            kwargs = {
                c.midi_id_field: c.midi_id,
                c.midi_value_field: value
            }
            dev.out_port.send(mido.Message(c.midi_type,**kwargs))

    def update_select(self, dev):
        c = self.dev_binding.find_control("select")
        if c and c.feedback:
            if self.target:
                if type(self.target) == ApplicationVolume:
                    value = c.down_value if (len(self.target.sessions) > 0) else c.up_value
                elif type(self.target) == DeviceVolume:
                    value = c.down_value
                else:
                    value = c.up_value
            else:
                value = c.up_value
            kwargs = {
                c.midi_id_field: c.midi_id,
                c.midi_value_field: value
            }
            dev.out_port.send(mido.Message(c.midi_type,**kwargs))

    def update_scribble(self, dev):
        """
        Returns a sysex message to update a scribble strip be sent via midi
        """
        if dev.scribble:
            dev.out_port.send(scribble(self.cid, color=self.color, top=self.name, bottom=self.level, inv_bot=True))

    def update_fader(self, dev):
        """
        Returns a midi message to update volume position
        """
        if self.touch_lock:
            return

        d = self.dev_binding
        c = d.find_control("volume")
        if c and c.feedback:
            kwargs = {
                c.midi_id_field: c.midi_id,
                c.midi_value_field: self.level
            }
            # print(f"Updating fader position for {self.cid} to {self.level}")
            dev.out_port.send(mido.Message(c.midi_type,**kwargs))

    def set_level(self, new_level):
        if int(new_level) == self.level:
            return False
        
        self.level = int(new_level)
        return True

    def update_level(self, dev):
        """
        Returns a midi message to update volume level display
        """
        d = self.dev_binding
        c = d.find_control("level")
        if c and c.feedback:
            if self.target or c.unset is None:
                display_level = int((self.level/127.0)*(c.max-c.min)+c.min)
            else:
                display_level = c.unset
            kwargs = {
                c.midi_id_field: c.midi_id,
                c.midi_value_field: display_level
            }
            dev.out_port.send(mido.Message(c.midi_type,**kwargs))

    def update_meter(self, dev):
        """
        Returns a midi message to update volume meter
        """
        d = self.dev_binding
        c = d.find_control("meter")
        if c and c.feedback:
            kwargs = {
                c.midi_id_field: c.midi_id,
                c.midi_value_field: self.level
            }
            dev.out_port.send(mido.Message(c.midi_type,**kwargs))

    def change_color(self, inc):
        """
        inc: 1 or -1 to represent direction
        Changes the color of the channel
        """
        colors = ["black","white","red","green","yellow","blue","cyan","magenta"]
        cur_index = colors.index(self.color)
        new_index = (cur_index+inc)%8
        self.color = colors[new_index]

    def set_level_from_float(self, value):
        prelim_level = int(127*value)
        if self.level == prelim_level:
            return False
        self.level = int(prelim_level) if prelim_level >= 0 else 0
        return True

    def get_level_from_target(self):
        self.set_level_from_float(self.target.get_volume())
        self.mute = bool(self.target.get_mute())

    def update_target_volume(self):
        self.target.set_volume(self.level/127)

    def toggle_mute(self):
        self.mute = not self.mute
        self.target.set_mute(self.mute)

    def increment_level(self, inc):
        new_level = self.level + inc
        if new_level < 0:
            new_level = 0
        elif new_level > 127:
            new_level = 127
        self.level = new_level

    def set_target_from_app_def(self, app_def):
        if app_def is None:
            self.unset_target()
            return

        if app_def.name == "Master":
            self.set_master()
            return

        self.name = app_def.name
        self.target = ApplicationVolume(app_def.name, app_def.sessions) 

        self.color = app_def.color
        self.get_level_from_target()
        print(f"Setting channel {self.cid} to {self.name} with {self.target.session_count()} sessions ")

    def unset_target(self):
        self.target = None
        self.name = "Unused"
        self.color = "black"
        self.level = 0
        print(f"Unsetting channel {self.cid}")

    def change_target(self, inc):
        apps = wh.get_applications_and_sessions()
        app_names = sorted(list(set(apps.keys()).difference(["Master"]))) + ["Master"]
        try:
            index = app_names.index(self.target.name) if self.target is not None else None
        except ValueError:
            index = None

        if index is None:
            if inc > 0:
                self.set_target_from_app_def(apps[app_names[0]])
            else:
                self.set_target_from_app_def(apps[app_names[-1]])
            
        else:
            pos = index + inc
            if pos >= len(app_names) or pos < 0:
                self.unset_target()
            else:
                self.set_target_from_app_def(apps[app_names[pos]])

    def set_master(self):
        self.name = "Master"
        self.color = "white"
        self.target = DeviceVolume(self.name, wh.get_master_volume_session())
        self.get_level_from_target()
        print(f"Setting channel {self.cid} to Master")

    def lock(self, lock, dev):
        if self.touch_lock and not lock:
            self.touch_lock = False
            self.update_fader(dev)
        else:
            self.touch_lock = lock

    def update_status(self, volume, mute, dev):
        self.mute = mute
        if self.set_level_from_float(volume):
            self.update_display(dev, fader=True)

    def refresh_sessions(self, dev):
        apps = wh.get_applications_and_sessions()
        if self.target.name not in apps:
            self.target.sessions = []
            self.level = 0
            self.mute = False
            print(f"Removing dead sessions for {self.target.name}")
        else:
            self.target.sessions = apps[self.target.name].sessions
            self.get_level_from_target()
        self.update_display(dev, fader=True)
