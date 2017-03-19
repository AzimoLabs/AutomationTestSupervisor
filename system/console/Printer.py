import datetime

from system.console import Color


def error(tag, message):
    print(Color.RED + '[{:%H:%M:%S}] - '.format(datetime.datetime.now()) + tag + " " + message + Color.END)


def system_message(tag, message):
    print(Color.BLUE + '[{:%H:%M:%S}] - '.format(datetime.datetime.now()) + tag + " " + message + Color.END)


def message_highlighted(tag, message, highlighted_message):
    print(Color.BLUE + '[{:%H:%M:%S}] - '.format(
        datetime.datetime.now()) + tag + " " + message + Color.GREEN + highlighted_message + Color.END)


def step(tag, message):
    print("\n" + Color.YELLOW + '[{:%H:%M:%S}] - '.format(datetime.datetime.now()) + tag + " " + message + Color.END)


def console_highlighted(tag, message, cmd):
    print(Color.BLUE + '[{:%H:%M:%S}] - '.format(datetime.datetime.now())
          + tag + " " + message + Color.GOLD + cmd + Color.END)


def console(message, end):
    print(Color.DARK_PURPLE + '[{:%H:%M:%S}] - '.format(datetime.datetime.now()) + message + Color.END, end=end)


def empty_line():
    print("")
