from console.Printer import *
import subprocess
import threading

TAG = "TestThread:"


class TestThread(threading.Thread):
    def __init__(self, cmd):
        super().__init__()

        self.cmd = cmd
        self.is_finished = False

    def run(self):
        try:
            print_console_highlighted(TAG, "Executing shell command: ", self.cmd)
            with subprocess.Popen(self.cmd, shell=True, stdout=subprocess.PIPE, bufsize=1,
                                  universal_newlines=True) as p:
                output = ""
                for line in p.stdout:
                    print_console(line, end='')
                    output += line

            if p.returncode != 0:
                raise Exception(p.returncode, p.args)
        finally:
            self.is_finished = True
