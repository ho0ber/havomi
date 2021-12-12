from channel import Channel, ChannelMap
from device import Device

def init_channels(dev):
    channel_map = ChannelMap([
        Channel(cid=0, name="Spotify", color="green",   level=0, dev_binding=dev.device_channels[0], target=None),
        Channel(cid=1, name="Chrome",  color="red",     level=0, dev_binding=dev.device_channels[1], target=None),
        Channel(cid=2, name="Discord", color="blue",    level=0, dev_binding=dev.device_channels[2], target=None),
        Channel(cid=3, name="Plex",    color="yellow",  level=0, dev_binding=dev.device_channels[3], target=None),
        Channel(cid=4, name="Apex",    color="cyan",    level=0, dev_binding=dev.device_channels[4], target=None),
        Channel(cid=5, name="StarC",   color="magenta", level=0, dev_binding=dev.device_channels[5], target=None),
        Channel(cid=6, name="Unused",  color="black",   level=0, dev_binding=dev.device_channels[6], target=None),
        Channel(cid=7, name="Master",  color="white",   level=0, dev_binding=dev.device_channels[7], target=None),
    ])

    for channel in channel_map.channels.values():
        dev.out_port.send(channel.update_scribble())
        dev.out_port.send(channel.update_level())
        dev.out_port.send(channel.update_fader())

    return channel_map

def start(event_queue, dev):
    channel_map = init_channels(dev)

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
