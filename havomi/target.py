from dataclasses import dataclass, field

@dataclass
class Target:
    """
    Targets are the applications or system volume channels to be controlled by the midi device.
    name: freeform string
    ttype: 'application' or 'master'
    session: an audio session with methods to get and set volume
    """
    # ttype: str
    name: str

    def session_count(self):
        return 1

@dataclass
class ApplicationVolume(Target):
    sessions: list[any] = field(default_factory=list)

    def get_volume(self):
        return min(session.SimpleAudioVolume.GetMasterVolume() for session in self.sessions)
    
    def get_mute(self):
        return bool(min(session.SimpleAudioVolume.GetMute() for session in self.sessions))

    def set_volume(self, level):
        for session in self.sessions:
            session.SimpleAudioVolume.SetMasterVolume(level, None)

    def set_mute(self, mute):
        for session in self.sessions:
            session.SimpleAudioVolume.SetMute(mute, None)

    def session_count(self):
        return len(self.sessions)

@dataclass
class SystemSoundsVolume(Target):
    session: any

    def get_volume(self):
        return self.session.SimpleAudioVolume.GetMasterVolume()
    
    def get_mute(self):
        return self. session.SimpleAudioVolume.GetMute()

    def set_volume(self, level):
        self.session.SimpleAudioVolume.SetMasterVolume(level, None)

    def set_mute(self, mute):
        self.session.SimpleAudioVolume.SetMute(mute, None)

@dataclass
class DeviceVolume(Target):
    session: any

    def get_volume(self):
        return self.session.GetMasterVolumeLevelScalar()

    def get_mute(self):
        return self.session.GetMute()

    def set_volume(self, level):
        self.session.SetMasterVolumeLevelScalar(level, None)

    
    def set_mute(self, mute):
        self.session.SetMute(mute, None)

