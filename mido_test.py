import mido
from dataclasses import dataclass

@dataclass
class Column:
    knob: int
    fader: int

names = mido.get_input_names()
print(names)
# # out_port = mido.open_output()

# with mido.open_input(names[0]) as inport:
#     for msg in inport:
#         # out_port.send(msg)
#         print(msg)

columns = [Column(knob=i+80,fader=i+70) for i in range(8)]
mapping = {}
for c in columns:
    mapping[f"control_change:{c.knob}"] = c
    mapping[f"control_change:{c.fader}"] = c
    
dev = "X-Touch-Ext X-TOUCH_INT"
with mido.open_input(dev) as inport, mido.open_output(dev) as outport:
    for msg in inport:
        # import pdb; pdb.set_trace()
        if msg.type == "control_change":
            
            outport.send(mido.Message('control_change', channel=0, control=msg.control-10, value=msg.value))
        print(msg)
            