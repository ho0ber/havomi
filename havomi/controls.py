from dataclasses import dataclass

@dataclass
class Control:
    type: str
    label: str
    midi_type: str
    midi_id_field: str
    midi_id: int
    midi_value_field: str
    feedback: bool

@dataclass
class Fader(Control):
    midi_value_min: int
    midi_value_max: int

@dataclass  
class RotaryEncoder(Control):
    increment_value: int
    decrement_value: int

@dataclass
class Button(Control):
    down_value: int = 127
    up_value: int = 0

@dataclass
class Meter(Control):
    pass
