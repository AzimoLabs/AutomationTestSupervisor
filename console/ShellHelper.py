from console.Printer import *
import subprocess

TAG = "ShellHelper:"


def execute_shell(cmd, show_cmd, monitor_output):
    if show_cmd:
        print_console_highlighted(TAG, "Executing shell command: ", cmd)
    with subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, bufsize=1, universal_newlines=True) as p:
        output = ""
        for line in p.stdout:
            if monitor_output:
                print_console(line, end='')
            output += line

    if p.returncode != 0:
        raise Exception(p.returncode, p.args)

    return output
