from os import system, name
from datetime import datetime, time
import platform
import subprocess
import os


# define our clear function
def clear():
    # for windows
    if name == 'nt':
        _ = system('cls')
    # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')


def is_time_between(begin_time, end_time, check_time=None):
    # If check time is not given, default to current UTC time
    # check_time = check_time or datetime.utcnow().time()
    if check_time:
        check_time = check_time.strftime("%H:%M")
    else:
        check_time = datetime.now().time().strftime("%H:%M")
    # check_time = check_time or datetime.now().time().strftime("%H:%M")

    if begin_time < end_time:
        return begin_time <= check_time <= end_time
    else: # crosses midnight
        return check_time >= begin_time or check_time <= end_time


def ping(host='8.8.8.8'):
    parameter = '-n' if platform.system().lower() == 'windows' else '-c'
    with open(os.devnull, 'w') as DEVNULL:
        try:
            subprocess.check_call(
                ['ping', parameter, '1', host],
                stdout=DEVNULL,  # suppress output
                stderr=DEVNULL
            )
            is_up = True
        except subprocess.CalledProcessError:
            is_up = False

