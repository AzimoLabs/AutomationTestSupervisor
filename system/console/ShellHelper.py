import subprocess

from system.console import Printer
from system.buffer import AdbCallBuffer

TAG = "ShellHelper:"


def execute_shell(cmd, show_cmd, monitor_output):

    if AdbCallBuffer.is_adb_cmd(cmd):
        AdbCallBuffer.report_adb_call()

    if show_cmd:
        Printer.console_highlighted(TAG, "Executing shell command: ", cmd)
    with subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, bufsize=1, universal_newlines=True) as p:
        output = ""
        for line in p.stdout:
            if monitor_output:
                Printer.console(line, end='')
            output += line

    if p.returncode != 0:
        raise Exception(p.returncode, p.args)

    return output
