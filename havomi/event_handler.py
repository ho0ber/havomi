from collections import defaultdict
import multiprocessing
from havomi import midi_listener
from havomi.device import Device
from havomi.target import ApplicationVolume, DeviceVolume
import havomi.windows_helpers as wh

def start(event_queue, dev, shared_map, channel_map, update_queue):
    """
    This is the main event handler loop. It listens to the multiprocessing event queue and reacts
    to events based on basic rules. The intent is for this code to be static for all devices, and
    for device config and application config (target bindings) to be the means by which we change
    behaviors of various controls.
    """
    print("Starting event_handler")
    active_modes = set()
    active_channel_modes = defaultdict(set)

    while True:
        event_type,event = event_queue.get()
        if event_type == "midi":
            match, value = channel_map.lookup(event)
            if match is not None:
                if match.control.func == "volume" and (match.channel.target is not None or "assign_mod" in active_modes):
                    if match.control.type == "fader":
                        if match.channel.set_level(match.control.normalize_level(value)):
                            match.channel.update_target_volume()
                            match.channel.update_display(dev)
                    elif match.control.type == "knob":
                        inc = match.control.get_increment(value)
                        if "assign_mod" in active_modes:
                            match.channel.change_target(inc)
                            match.channel.update_display(dev, fader=True)
                            channel_map.save()
                        else:
                            match.channel.increment_level(inc)
                            match.channel.update_target_volume()
                            match.channel.update_display(dev)

                # Assign session to a channel with a knob
                elif match.control.func == "assign":
                    inc = match.control.get_increment(value)
                    if "color_mod" in active_channel_modes[match.channel.cid]:
                        match.channel.change_color(inc)
                    else:
                        match.channel.change_target(inc)

                    channel_map.save()
                    match.channel.update_display(dev, fader=True)
                
                # Select session from foreground window
                elif match.control.func == "select" and match.control.down_value == value:
                    if match.channel.target:
                        match.channel.unset_target()
                    else:
                        app_def = wh.get_active_window_app_def()
                        match.channel.set_target_from_app_def(app_def)
                    channel_map.save()
                    match.channel.update_display(dev, fader=True)

                # Mute channel
                elif match.control.func == "mute" and match.control.down_value == value:
                    if match.channel.target:
                        match.channel.toggle_mute()
                        match.channel.update_display(dev)

                # Touch-lock channel
                elif match.control.func == "touch":
                    match.channel.lock(value == match.control.down_value, dev)

                if match.control.func.endswith("_mod"):
                    if value == match.control.down_value:
                        print(f"{match.channel.cid}:{match.control.func} enabled")
                        active_channel_modes[match.channel.cid].add(match.control.func)
                    else:
                        print(f"{match.channel.cid}:{match.control.func} disabled")
                        active_channel_modes[match.channel.cid].remove(match.control.func)
            else:
                match, value = shared_map.lookup(event)
                if match is not None:
                    if match.func == "quit":
                        print("Got quit button; quitting.")
                        break

                    elif match.func == "media_play_pause" and value == match.down_value:
                        wh.send_key("VK_MEDIA_PLAY_PAUSE")

                    elif match.func == "media_stop" and value == match.down_value:
                        wh.send_key("VK_MEDIA_STOP")

                    elif match.func == "media_prev" and value == match.down_value:
                        wh.send_key("VK_MEDIA_PREV_TRACK")

                    elif match.func == "media_next" and value == match.down_value:
                        wh.send_key("VK_MEDIA_NEXT_TRACK")

                    elif match.func.endswith("_mod"):
                        if value == match.down_value:
                            print(f"{match.func} enabled")
                            active_modes.add(match.func)
                        else:
                            print(f"{match.func} disabled")
                            active_modes.remove(match.func)

        if event_type == "system":
            for channel in channel_map.channels.values():
                if type(channel.target) == ApplicationVolume:
                    if channel.target.name in event["apps"]:
                        channel_sessions = set(s.InstanceIdentifier for s in channel.target.sessions)
                        app_sessions = set(a["identifier"] for a in event["apps"][channel.target.name])
                        if channel_sessions != app_sessions:
                            channel.refresh_sessions(dev)
                        else:
                            volume = min(a["level"] for a in event["apps"][channel.target.name])
                            mute = all(bool(a["mute"]) for a in event["apps"][channel.target.name])
                            channel.update_status(volume, mute, dev)
                            channel.update_display(dev)
                    elif channel.target.sessions:
                        channel.refresh_sessions(dev)
                elif type(channel.target) == DeviceVolume:
                    if channel.target.name == "Master":
                        channel.update_status(event["master"]["level"], event["master"]["mute"], dev)
                        channel.update_display(dev)

        if event_type == "interface":
            if event["action"] == "quit":
                # midi_listener_process.terminate()
                print("Got quit from menu; quitting.")
                return("quit", None)
            elif event["action"] == "assign":
                print(f"Got assign event: {event}")
                channel = channel_map.channels[event["channel"]]
                if event["app"] == "Master":
                    channel.set_master()
                else:
                    channel.set_target_from_app_def(wh.get_app_def_from_name(event["app"]))
                channel_map.save()
                channel.update_display(dev, fader=True)
            elif event["action"] == "unassign":
                print(f"Got unassign event: {event}")
                channel = channel_map.channels[event["channel"]]
                channel.unset_target()
                channel_map.save()
                channel.update_display(dev, fader=True)
            elif event["action"] == "change_dev":
                # This should be refactored out eventually, but for now we can explicitly overwrite "dev" and the maps and
                # then restart the midi_listener.
                print(f"Got signal to change device: {event}")
                return ("restart_midi", event["dev_info"])
                # midi_listener.stop(dev, midi_listener_process)
                dev.out_port.close()
                midi_listener_process.terminate()
                midi_listener_process.join()
                print("terminated midi listener")
                # shared_map, channel_map, dev, midi_listener_process = midi_listener.init(event["dev_info"], event_queue)

                dev = Device(event["dev_info"])
                shared_map, channel_map = dev.init_channels()
                print("inited device")
                if channel_map.load():
                    for channel in channel_map.channels.values():
                        channel.update_display(dev, fader=True)
                midi_listener_process = multiprocessing.Process(target = midi_listener.start, args=(event_queue, dev.in_name))
                midi_listener_process.start()

        # Update systray menu state after any event
        update_queue.put(("state", channel_map.get_state()))
    print("Did I get here?")
