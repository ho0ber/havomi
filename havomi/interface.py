from PyInquirer import prompt, Separator
from pprint import pprint
import mido
import mido.backends.rtmidi
from os.path import join, dirname, realpath
from os import listdir

def get_config():
    devices_path = join(dirname(dirname(realpath(__file__))),"devices")

    inputs = mido.get_input_names()
    outputs = mido.get_output_names()
    devices = [x for x in listdir(devices_path) if x.endswith(".yaml")]
    questions = [
        {
            'type': 'list',
            'name': 'input',
            'message': 'Choose your input device',
            'choices': inputs
        },
        {
            'type': 'list',
            'name': 'output',
            'message': 'Choose your output device',
            'choices': outputs
        },
        {
            'type': 'list',
            'name': 'device',
            'message': 'Choose your device config',
            'choices': devices + ["Custom"]
        },
    ]
    answers = prompt(questions)

    if answers["device"] == "Custom":
        question = [
            {
                'type': 'input',
                'name': 'device',
                'message': 'Path to device config:',
            }
        ]
        d_answer = prompt(question)
        answers["device"] = d_answer["device"]
    else:
        answers["device"] = join(devices_path, answers["device"])

    return answers