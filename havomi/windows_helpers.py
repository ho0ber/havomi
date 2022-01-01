import win32gui, win32process
from pycaw.pycaw import AudioUtilities
import psutil

def get_active_window_session():
    hwnd = win32gui.GetForegroundWindow()
    tid, current_pid = win32process.GetWindowThreadProcessId(hwnd)
    process_name = psutil.Process(current_pid).name()
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        if session.Process and session.Process.name() == process_name:
            return session
