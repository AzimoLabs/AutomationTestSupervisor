import time
import subprocess
import threading

from system.console import (
    Printer,
    Color
)


class TestThread(threading.Thread):
    TAG = "TestThread:"

    def __init__(self, cmd, device_name):
        super().__init__()

        self.cmd = cmd
        self.device_name = device_name
        self.is_finished = False

    def run(self):
        try:
            Printer.console_highlighted(self.TAG, "Executing shell command: ", self.cmd)
            with subprocess.Popen(self.cmd, shell=True, stdout=subprocess.PIPE, bufsize=1,
                                  universal_newlines=True) as p:
                output = ""
                for line in p.stdout:
                    Printer.console(line, end='')
                    output += line

            if p.returncode != 0:
                raise Exception(p.returncode, p.args)
        finally:
            self.is_finished = True


class ApkInstallThread(threading.Thread):
    TAG = "ApkInstallThread:"

    def __init__(self, device, apk_path):
        super().__init__()

        self.device = device
        self.apk_path = apk_path
        self.is_finished = False
        self.install_time = 0

    def run(self):
        start_time = int(round(time.time() * 1000))

        self.device.install_apk(self.apk_path)

        end_time = int(round(time.time() * 1000))
        self.install_time = (end_time - start_time) / 1000
        self.is_finished = True

        Printer.system_message(self.TAG, ".*apk " + Color.GREEN + "'" + self.apk_path + "'" + Color.BLUE
                               + " was successfully installed on device " + Color.GREEN + "'" + self.device.adb_name
                               + "'" + Color.BLUE + ". It took " + Color.GREEN + str(self.install_time) + Color.BLUE
                               + " seconds.")
