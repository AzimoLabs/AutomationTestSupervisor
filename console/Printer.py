import datetime

from console.Color import *


def print_error(tag, message):
    print(Color.RED + '[{:%H:%M:%S}] - '.format(datetime.datetime.now()) + tag + " " + message + Color.END)


def print_message(tag, message):
    print(Color.BLUE + '[{:%H:%M:%S}] - '.format(datetime.datetime.now()) + tag + " " + message + Color.END)


def print_message_highlighted(tag, message, highlighted_message):
    print(Color.BLUE + '[{:%H:%M:%S}] - '.format(
        datetime.datetime.now()) + tag + " " + message + Color.GREEN + highlighted_message + Color.END)


def print_step(tag, message):
    print("\n" + Color.YELLOW + '[{:%H:%M:%S}] - '.format(datetime.datetime.now()) + tag + " " + message + Color.END)


def print_console_highlighted(tag, message, cmd):
    print(Color.BLUE + '[{:%H:%M:%S}] - '.format(datetime.datetime.now())
          + tag + " " + message + Color.GOLD + cmd + Color.END)


def print_console(message, end):
    print(Color.DARK_PURPLE + '[{:%H:%M:%S}] - '.format(datetime.datetime.now()) + message + Color.END, end=end)


def empty_line():
    print("")
