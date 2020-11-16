import platform
import subprocess
import shlex


def is_linux_platform():
    return "Linux" in platform.platform()


def get_profile_path():
    if "Linux" in platform.platform():
        profile_path = "/home/mrafay/.config/google-chrome"
    else:
        profile_path = r"C:\Users\user\AppData\Local\Google\Chrome\User Data"
    return profile_path


def get_driver_path():
    return r"C:\Users\user\Downloads\chromedriver.exe"


def kill_process(process_name):
    if is_linux_platform():
        command = f"taskkill /f /im {process_name}"
    else:
        command = f"killall {process_name}"
    return subprocess.call(shlex.split(command))

