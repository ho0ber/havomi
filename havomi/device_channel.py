from dataclasses import dataclass, field

@dataclass
class DeviceChannel:
    """
    Device channels are the sets of controls that are grouped together for the purposes of
    controlling a single target (application or audio device).
    """
    cid: int
    controls: field(default_factory=list)

    def find_control(self, func):
        for control in self.controls:
            if control.func == func:
                return control
