import time
import havomi.windows_helpers as wh

def start(event_queue):
    """
    This is the entry point for the system listener process. It listens to system events such as
    volume changes and sends events to the event_queue to update motorized faders and other
    feedback controls on the device.
    """
    master = wh.get_master_volume_session()
    while True:
        time.sleep(1)
        apps = wh.get_applications_and_sessions()
        app_volumes = {}
        for app in apps.values():
            if app.name != "Master":
                app_volumes[app.name] = [{
                    "identifier": session.InstanceIdentifier,
                    "level": session.SimpleAudioVolume.GetMasterVolume(),
                    "mute": session.SimpleAudioVolume.GetMute()
                } for session in app.sessions]

        event = {
            "apps": app_volumes,
            "master": {"level": master.GetMasterVolumeLevelScalar(), "mute": master.GetMute()}
        }
        event_queue.put(("system", event))
