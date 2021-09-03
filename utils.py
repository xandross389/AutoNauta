from os import system, name
from datetime import datetime, time


# define our clear function
def clear():
    # for windows
    if name == 'nt':
        _ = system('cls')
    # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')


# def str2time(strtime, format=None):
#     # # Function to convert string to datetime
#     # format = '%b %d %Y %I:%M%p'  # The format
#     # datetime_str = datetime.datetime.strptime(date_time, format)
#     #
#     #     return datetime_str
#     #
#     # # Driver code
#     # date_time = 'Dec 4 2018 10:07AM'
#     # print(convert(date_time))
#     import time
#
#     # Function to convert string to datetime
#     datetime_str = time.mktime(strtime)
#
#     format = format or "%H:%M"  # The format
#     dateTime = time.strftime(format, time.gmtime(datetime_str))
#     return dateTime
#
#     # Driver code
#     # date_time = (2018, 12, 4, 10, 7, 00, 1, 48, 0)
#     # print(convert(date_time))


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

