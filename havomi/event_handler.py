
def start(event_queue, dev, channel_map):
    while True:
        event_type,event = event_queue.get()
        # print(f"got event: {event}")
        if event_type == "midi":
            match, value = channel_map.lookup(event)
            if match is not None:
                if match.type == "fader":
                    match.channel.level = value
                    dev.out_port.send(match.channel.update_scribble())
                    dev.out_port.send(match.channel.update_level())
                elif match.type == "knob":
                    inc = {1:-1, 65:+1, None:0}.get(value)
                    match.channel.change_color(inc)
                    dev.out_port.send(match.channel.update_scribble())

        if event_type == "system":
            cid,level = event["channel"], event["level"]
            channel_map.channels[cid].level = level
            dev.out_port.send(channel_map.channels[cid].update_scribble())
            dev.out_port.send(channel_map.channels[cid].update_level())
            dev.out_port.send(channel_map.channels[cid].update_fader())
