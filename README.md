# Havomi
**Havomi** - **Ha**rdware **Vo**lume **Mi**xer

### ⚠️ This project is still in the early stages. If you require a more stable tool, please use its predecessors, or consider one of the similar projects below. ⚠️

## Description
This is a rewrite of [NK2Tray](https://github.com/ho0ber/nk2tray), which is a rewrite of [nk2-audio](https://github.com/ho0ber/nk2-audio).

For some backstory on why I am beginning yet another rewrite of the same project, here are the pros and cons of the three versions:

### nk2-audio
This was a prototype only, written in autohotkey. It was difficult to debug and nearly impossible to improve.

### NK2Tray
This was an attempt at a self-sustaining open-source version of the project. Written as a native app in C#, performance was good and access to windows API functions and UI elements was relatively straight-forward.

If I was a full-time C# and windows developer, this would have been an easy win. Unfortunately, refactoring and debugging this project was difficult for me, and I rarely had time to lean in and help the project because it required a very different development environment setup than my normal work. Additionally, contributors were hard to come by and cross-platform support was less than ideal.

### Havomi
The goal of Havomi is to provide all of the same functionality as NK2Tray, but in a language that I am more comfortable in, and for which it will be easier to find contributors. Additionally, the long-term goal of support for OSX and Linux is well served by python.

An additional improvement planned for Havomi is significantly simplified device support configuration, through the use of verbose but straightforward YAML configs, rather than device configuration being written as code.

The biggest advantage, by far, is that I will be able to personally contribute significantly more without significant effort. I'll be able to identify and fix many bugs without needing to change operating systems, and automated builds will enable quick release of bug fixes, even if I'm away from a Windows box.

## Getting Involved
To help test or contribute, I encourage you to join our discord: https://discord.gg/BtVTYxp

## Download
To download a development build, **log in** to a github account and then go to the [Build executable actions page](https://github.com/ho0ber/havomi/actions/workflows/build.yml). Click the most recent completed workflow run and scroll to the bottom to find the Windows-Binary artifact, and download.

## Similar Projects
* [**MIDI Mixer**](https://www.midi-mixer.com/) - Not open source, but free. Actively maintained.
* [**MidiManager**](https://jitse-ten-hove.itch.io/midimanager) - Not open source, but free. Actively maintained.
* [**deej**](https://github.com/omriharel/deej) - Open source. A similar project for those interested in building their own mixer.

## Development & Environment Setup
### Running locally on Windows
* `python3.9 -m venv venv`
* `.\venv\Scripts\activate.bat`
* `pip install -r requirements.txt`
* `python main.py`

### Building locally on Windows
* `python3.9 -m venv venv`
* `.\venv\Scripts\activate.bat`
* `pip install -r requirements.txt`
* `pip install -r build_requirements.txt`
* `.\scripts\build.bat`
