from dataclasses import dataclass
from pycaw.pycaw import AudioUtilities

@dataclass
class Target:
    """
    Targets are the applications or system volume channels to be controlled by the midi device.
    name: freeform string
    ttype: 'application' or 'master'
    session: an audio session with methods to get and set volume
    """
    name: str
    ttype: str
    session: any