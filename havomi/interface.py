from PyInquirer import prompt, Separator
from pprint import pprint
import mido
import mido.backends.rtmidi
from os.path import join, dirname, realpath
from os import listdir
import platform
import yaml

def get_device_file():
    devices_path = join(dirname(dirname(realpath(__file__))),"devices")
    devices = [x for x in listdir(devices_path) if x.endswith(".yaml")]
    questions = [
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

    return answers["device"]


def get_config():
    device_filename = get_device_file()
    os = platform.system()

    inputs = mido.get_input_names()
    outputs = mido.get_output_names()

    with open(device_filename) as device_file:
        config = yaml.safe_load(device_file.read())

    if os.lower() == "windows":
        input_dev = config.get("device_names",{}).get("windows",{}).get("input")
        output_dev = config.get("device_names",{}).get("windows",{}).get("output")

    questions = []
    if input_dev is None or input_dev not in inputs:
        questions.append({
            'type': 'list',
            'name': 'input',
            'message': 'Choose your input device',
            'choices': inputs
        })
    if output_dev is None or output_dev not in outputs:
        questions.append({
            'type': 'list',
            'name': 'output',
            'message': 'Choose your output device',
            'choices': outputs
        })


    answers = prompt(questions) if questions else {}
    if input_dev:
        answers["input"] = input_dev
    if output_dev:
        answers["output"] = output_dev
    answers["device"] = device_filename

    return answers
