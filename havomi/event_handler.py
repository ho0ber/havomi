import mido
from channel import Channel, ChannelMap

def init_channels(out_port):
    channel_map = ChannelMap([
        Channel(cid=0, fid=70, kid=80, lid=90, name="Spotify", color="green",   level=0),
        Channel(cid=1, fid=71, kid=81, lid=91, name="Chrome",  color="red",     level=0),
        Channel(cid=2, fid=72, kid=82, lid=92, name="Discord", color="blue",    level=0),
        Channel(cid=3, fid=73, kid=83, lid=93, name="Plex",    color="yellow",  level=0),
        Channel(cid=4, fid=74, kid=84, lid=94, name="Apex",    color="cyan",    level=0),
        Channel(cid=5, fid=75, kid=85, lid=95, name="StarC",   color="magenta", level=0),
        Channel(cid=6, fid=76, kid=86, lid=96, name="Unused",  color="black",   level=0),
        Channel(cid=7, fid=77, kid=87, lid=97, name="Master",  color="white",   level=0),
    ])

    for channel in channel_map.channels.values():
        out_port.send(channel.update_scribble())
        out_port.send(channel.update_level())
        out_port.send(channel.update_fader())

    return channel_map

def start(event_queue):
    dev = "X-Touch-Ext X-TOUCH_INT"
    with mido.open_output(dev) as out_port:
        channel_map = init_channels(out_port)

        while True:
            event_type,event = event_queue.get()
            print(f"got event: {event}")
            if event_type == "midi":
                match, value = channel_map.lookup(event)
                if match is not None:
                    if match.type == "fader":
                        match.channel.level = value
                        out_port.send(match.channel.update_scribble())
                        out_port.send(match.channel.update_level())
                    elif match.type == "knob":
                        inc = {1:-1, 65:+1, None:0}.get(value)
                        match.channel.change_color(inc)
                        out_port.send(match.channel.update_scribble())

                    
            if event_type == "system":
                cid,level = event["channel"], event["level"]
                channel_map.channels[cid].level = level
                out_port.send(channel_map.channels[cid].update_scribble())
                out_port.send(channel_map.channels[cid].update_level())
                out_port.send(channel_map.channels[cid].update_fader())
