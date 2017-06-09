import sys

from error.Exceptions import LauncherFlowInterruptedException

from system.console import (
    Printer,
    Color
)

NUMBER = "1.0-beta"
MIN_PYTHON_VER = (3, 6)


def info():
    Printer.system_message("", "AutomationTestSupervisor version: " + Color.GREEN + NUMBER + Color.BLUE + ".")


def python_check():
    if sys.version_info >= MIN_PYTHON_VER:
        Printer.system_message("", "Minimum Python version requirement met! Your version: " + Color.GREEN
                               + str(sys.version_info) + Color.BLUE + ".")

    else:
        message = ("Invalid Python version. Please use at least Python " + str(MIN_PYTHON_VER[0]) + "."
                   + str(MIN_PYTHON_VER[1]) + ".")
        raise LauncherFlowInterruptedException("", message)
