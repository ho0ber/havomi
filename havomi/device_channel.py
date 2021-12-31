from dataclasses import dataclass, field

@dataclass
class DeviceChannel:
    cid: int
    controls: field(default_factory=list)

    def find_control(self, func):
        for control in self.controls:
            if control.func == func:
                return control
