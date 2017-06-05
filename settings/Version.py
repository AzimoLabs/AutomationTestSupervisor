from system.console import (
    Printer,
    Color
)

NUMBER = "1.0-beta"


def info():
    Printer.system_message("", "Version: " + Color.GREEN + NUMBER + Color.BLUE + ".")
