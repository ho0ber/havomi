import hashlib
import mido
import mido.backends.rtmidi
from dataclasses import dataclass
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

from havomi.device import Device, DeviceChannel
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
    color: str
    dev_binding: DeviceChannel
    target: Target

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
        d = self.dev_binding
        c = d.find_control("volume")
        if c.feedback:
            kwargs = {
                c.midi_id_field: c.midi_id,
                c.midi_value_field: self.level
            }
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
            display_level = int((self.level/127.0)*(c.max-c.min)+c.min)
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
        prelim_level = 127*value
        self.level = int(prelim_level) if prelim_level >= 0 else 0

    def get_level_from_target(self):
        if type(self.target) == ApplicationVolume:
            self.set_level_from_float(self.target.sessions[0].SimpleAudioVolume.GetMasterVolume())
        elif type(self.target) == DeviceVolume:
            self.set_level_from_float(self.target.session.GetMasterVolumeLevelScalar())

    def update_target_volume(self):
        if type(self.target) == ApplicationVolume:
            for session in self.target.sessions:
                session.SimpleAudioVolume.SetMasterVolume(self.level/127, None)
        elif type(self.target) == SystemSoundsVolume:
            self.target.session.SimpleAudioVolume.SetMasterVolume(self.level/127, None)
        elif type(self.target) == DeviceVolume:
            self.target.session.SetMasterVolumeLevelScalar(self.level/127, None)

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
        
        if not app_def.sessions:
            self.unset_target()
            return
        
        self.name = app_def.name
        self.target = ApplicationVolume(app_def.name, app_def.sessions)
        self.color = app_def.color
        self.get_level_from_target()
        print(f"Setting channel {self.cid} to {self.name} with {len(self.target.sessions)} sessions ")

    def unset_target(self):
        self.target = None
        self.name = "Unused"
        self.color = "black"
        self.level = 0
        print(f"Unsetting channel {self.cid}")

    def change_target(self, inc):
        apps = wh.get_applications_and_sessions()
        app_names = sorted(apps.keys())
        index = app_names.index(self.target.name) if self.target is not None else None

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
        self.level = int(self.target.session.GetMasterVolumeLevelScalar()*127)
