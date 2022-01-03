import mido
import mido.backends.rtmidi
import time


if __name__ == "__main__":
        with mido.open_output("X-TOUCH MINI 2") as out_port:
            c = 48
            for v in [32, 33, 34, 35,36,37,38,39,40,41,42,43, 44]:
                msg = mido.Message("control_change", control=c, value=v)
                print(f"Sending {msg}")
                out_port.send(msg)
                time.sleep(0.2)
