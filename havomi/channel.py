from dataclasses import dataclass
import hashlib
import mido
import mido.backends.rtmidi
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

from havomi.device import DeviceChannel
from havomi.target import Target
from havomi.scribble import scribble

@dataclass
class Channel:
    cid: int
    name: str
    level: int
    color: str
    dev_binding: DeviceChannel
    target: Target

    def update_scribble(self):
        return scribble(self.cid, color=self.color, top=self.name, bottom=self.level, inv_bot=True)

    def update_fader(self):
        d = self.dev_binding
        c = d.find_control("volume")
        if c.feedback:
            kwargs = {
                c.midi_id_field: c.midi_id,
                c.midi_value_field: self.level
            }
            return mido.Message(c.midi_type,**kwargs)

    def update_level(self):
        d = self.dev_binding
        c = d.find_control("level")
        if c.feedback:
            kwargs = {
                c.midi_id_field: c.midi_id,
                c.midi_value_field: self.level
            }
            return mido.Message(c.midi_type,**kwargs)

    def change_color(self, inc):
        colors = ["black","white","red","green","yellow","blue","cyan","magenta"]
        cur_index = colors.index(self.color)
        new_index = (cur_index+inc)%8
        self.color = colors[new_index]

    def set_level_from_float(self, value):
        prelim_level = 127*value
        self.level = int(prelim_level) if prelim_level >= 0 else 0

    def get_level_from_target(self):
        self.set_level_from_float(self.target.session.SimpleAudioVolume.GetMasterVolume())

    def update_target_volume(self):
        if self.target.ttype == "application":
            self.target.session.SimpleAudioVolume.SetMasterVolume(self.level/127, None)
        elif self.target.ttype == "master":
            self.target.session.SetMasterVolumeLevelScalar(self.level/127, None)

    def set_target_from_session(self, session):
        self.name = session.Process.name() if session.Process else "?"
        self.target = Target(self.name, "application", session)
        self.color = ["red","green","yellow","blue","cyan","magenta"][int(hashlib.md5(session.InstanceIdentifier.encode('utf-8')).hexdigest(),16)%6%6] if session.Process else "white"
        self.get_level_from_target()

    def unset_target(self):
        self.target = None
        self.name = "Unused"
        self.color = "black"
        self.level = 0
    
    def find_session(self, session_list):
        if self.target is None:
            return None
        
        for i,s in enumerate(session_list):
            if self.target.session.InstanceIdentifier is None:
                if s.InstanceIdentifier is None:
                    return i
            elif s.InstanceIdentifier == self.target.session.InstanceIdentifier:
                return i
        
        return None


    def change_target(self, inc):
        sessions = AudioUtilities.GetAllSessions()
        index = self.find_session(sessions)

        if index is None:
            if inc > 0:
                self.set_target_from_session(sessions[0])
            else:
                self.set_target_from_session(sessions[-1])
            
        else:
            pos = index + inc
            if pos >= len(sessions) or pos < 0:
                self.unset_target()
            else:
                self.set_target_from_session(sessions[pos])

    def set_master(self):
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        self.name = "Master"
        self.target = Target(self.name, "master", volume)
        self.color = "white"
        self.level = int(volume.GetMasterVolumeLevelScalar()*127)
    