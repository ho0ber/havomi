# pip install pywin32
# pip install psutil
# from win32gui import GetWindowText, GetForegroundWindow
import win32gui, win32process
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

def get_active_window_session():
    hwnd = win32gui.GetForegroundWindow()
    _, current_pid = win32process.GetWindowThreadProcessId(hwnd)
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        if session.Process and session.Process.pid == current_pid:
            return session
