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

@dataclass
class ApplicationVolume(Target):
    sessions: list[any] = field(default_factory=list)

@dataclass
class SystemSoundsVolume(Target):
    session: any

@dataclass
class DeviceVolume(Target):
    session: any
