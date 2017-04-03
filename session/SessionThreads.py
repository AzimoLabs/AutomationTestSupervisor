import time
import re
import subprocess
import threading

from error.Exceptions import LauncherFlowInterruptedException

from system.console import ShellHelper
from system.console import (
    Printer,
    Color
)


# TODO RETRY ON ADB FAILURES
class TestThread(threading.Thread):
    TAG = "TestThread<device_adb_name>:"

    def __init__(self, launch_tests_cmd, device):
        super().__init__()

        self.launch_tests_cmd = launch_tests_cmd

        self.device = device
        self.TAG = self.TAG.replace("device_adb_name", device.adb_name)

        self.is_finished = False

    def run(self):
        try:
            Printer.console_highlighted(self.TAG, "Executing shell command: ", self.launch_tests_cmd)
            with subprocess.Popen(self.launch_tests_cmd, shell=True, stdout=subprocess.PIPE, bufsize=1,
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
    TAG = "ApkInstallThread<device_adb_name>:"

    def __init__(self, dump_badging_cmd, device, apk_name, apk_path):
        super().__init__()
        self.dump_badging_cmd = dump_badging_cmd

        self.device = device
        self.TAG = self.TAG.replace("device_adb_name", device.adb_name)

        self.apk_name = apk_name
        self.apk_path = apk_path

        self.is_finished = False
        self.install_time = 0

    def run(self):
        start_time = int(round(time.time() * 1000))

        package = self._get_apk_package()
        installed_packages_str = self.device.get_installed_packages()

        if package in installed_packages_str:
            Printer.system_message(self.TAG, "Package " + Color.GREEN + "'" + package + "'" + Color.BLUE +
                                   " is currently installed on device '" + Color.GREEN + self.device.adb_name
                                   + Color.BLUE + "'. Removing from device...")
            self.device.uninstall_package(package)
        else:
            Printer.system_message(self.TAG, "Package " + Color.GREEN + "'" + package + "'" + Color.BLUE +
                                   " was not found on device '" + Color.GREEN + self.device.adb_name + Color.BLUE +
                                   "'.")

        Printer.system_message(self.TAG, "Installing .*apk file...")
        self.device.install_apk(self.apk_path)

        end_time = int(round(time.time() * 1000))
        self.install_time = (end_time - start_time) / 1000

        Printer.system_message(self.TAG, ".*apk " + Color.GREEN + "'" + self.apk_path + "'" + Color.BLUE
                               + " was successfully installed on device " + Color.GREEN + "'" + self.device.adb_name
                               + "'" + Color.BLUE + ". It took " + Color.GREEN + str(self.install_time) + Color.BLUE
                               + " seconds.")

        self.is_finished = True

    def _get_apk_package(self):
        dump = ShellHelper.execute_shell(self.dump_badging_cmd, False, False)
        regex_result = re.findall("package: name='(.+?)'", dump)
        if regex_result:
            package = str(regex_result[0])
            Printer.message_highlighted(self.TAG, "Package that is about to be installed: ", package)
        else:
            message = "Unable to find package of .*apk file: " + self.apk_name
            raise LauncherFlowInterruptedException(self.TAG, message)
        return package
