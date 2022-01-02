import havomi.windows_helpers as wh

def start(event_queue, dev, channel_map):
    """
    This is the main event handler loop. It listens to the multiprocessing event queue and reacts
    to events based on basic rules. The intent is for this code to be static for all devices, and
    for device config and application config (target bindings) to be the means by which we change
    behaviors of various controls.
    """
    while True:
        event_type,event = event_queue.get()
        if event_type == "midi":
            match, value = channel_map.lookup(event)
            if match is not None:
                if match.control.func == "volume" and match.channel.target is not None:
                    if match.control.type == "fader":
                        if match.channel.set_level(match.control.normalize_level(value)):
                            match.channel.update_target_volume()
                            match.channel.update_scribble(dev)
                            match.channel.update_level(dev)
                            match.channel.update_meter(dev)
                    elif match.control.type == "knob":
                        inc = match.control.get_increment(value)
                        match.channel.increment_level(inc)
                        match.channel.update_target_volume()
                        match.channel.update_scribble(dev)
                        match.channel.update_level(dev)
                        match.channel.update_meter(dev)

                # Assign session to a channel with a knob
                elif match.control.func == "assign":
                    inc = match.control.get_increment(value)
                    match.channel.change_target(inc)
                    match.channel.update_scribble(dev)
                    match.channel.update_level(dev)
                    match.channel.update_meter(dev)
                    match.channel.update_fader(dev)
                
                # Quit by hitting select on master channel
                elif match.control.func == "select" and match.channel.target and match.channel.target.name == "Master":
                    print("Got quit button; quitting.")
                    break
                
                # Select session from foreground window
                elif match.control.func == "select" and match.control.down_value == value:
                    if match.channel.target:
                        match.channel.unset_target()
                    else:
                        app_def = wh.get_active_window_app_def()
                        match.channel.set_target_from_app_def(app_def)
                    match.channel.update_scribble(dev)
                    match.channel.update_level(dev)
                    match.channel.update_meter(dev)
                    match.channel.update_fader(dev)

        if event_type == "system":
            cid,level = event["channel"], event["level"]
            channel_map.channels[cid].level = level
            channel_map.channels[cid].update_scribble(dev)
            channel_map.channels[cid].update_level(dev)
            channel_map.channels[cid].update_fader(dev)
