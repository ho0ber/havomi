from dataclasses import dataclass
from pycaw.pycaw import AudioUtilities

@dataclass
class Target:
    name: str
    ttype: str
    session: any