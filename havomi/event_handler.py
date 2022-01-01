from havomi.windows_helpers import get_active_window_session

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
                # Volume change input
                if match.control.func == "volume" and match.channel.target is not None:
                    if match.control.type == "fader":
                        match.channel.level = value
                        match.channel.update_target_volume()
                    elif match.control.type == "knob":
                        inc = match.control.get_increment(value)
                        match.channel.increment_level(inc)
                    dev.out_port.send(match.channel.update_scribble())
                    dev.out_port.send(match.channel.update_level())
                    dev.out_port.send(match.channel.update_meter())

                # Assign session to a channel with a knob
                elif match.control.func == "assign":
                    inc = match.control.get_increment(value)
                    match.channel.change_target(inc)
                    dev.out_port.send(match.channel.update_scribble())
                    dev.out_port.send(match.channel.update_level())
                    dev.out_port.send(match.channel.update_meter())
                    dev.out_port.send(match.channel.update_fader())
                
                # Quit by hitting select on master channel
                elif match.control.func == "select" and match.channel.target.ttype == "master":
                    break
                
                # Select session from foreground window
                elif match.control.func == "select":
                    session = get_active_window_session()
                    match.channel.set_target_from_session(session)
                    dev.out_port.send(match.channel.update_scribble())
                    dev.out_port.send(match.channel.update_level())
                    dev.out_port.send(match.channel.update_meter())
                    dev.out_port.send(match.channel.update_fader())

        if event_type == "system":
            cid,level = event["channel"], event["level"]
            channel_map.channels[cid].level = level
            dev.out_port.send(channel_map.channels[cid].update_scribble())
            dev.out_port.send(channel_map.channels[cid].update_level())
            dev.out_port.send(channel_map.channels[cid].update_fader())
