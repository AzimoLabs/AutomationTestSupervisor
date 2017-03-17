from console.Printer import *
from console.Color import *

import threading

import time

TAG = "ApkInstallThread:"


class ApkInstallThread(threading.Thread):
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
        print_message(TAG, ".*apk " + Color.GREEN + "'" + self.apk_path + "'" + Color.BLUE
                      + " was successfully installed on device " + Color.GREEN + "'" + self.device.adb_name + "'"
                      + Color.BLUE + ". It took " + Color.GREEN + str(self.install_time) + Color.BLUE + " seconds.")
        self.is_finished = True
