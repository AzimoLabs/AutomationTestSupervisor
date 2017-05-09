import time
import re
import subprocess
import threading

from error.Exceptions import LauncherFlowInterruptedException

from session.SessionModels import (
    TestLogCat,
    TestLogCatLine,
    TestSummary
)

from system.console import ShellHelper
from system.console import (
    Printer,
    Color
)


class TestLogCatMonitorThread(threading.Thread):
    TAG = "TestLogCatMonitorThread<device_adb_name>:"

    TEST_STARTED = "TestRunner: started:"
    TEST_FINISHED = "TestRunner: finished:"

    LOG_LEVELS = ["D", "I", "W", "V", "E"]

    DATE_INDEX = 0
    TIME_INDEX = 1
    PID_INDEX = 2
    LEVEL_INDEX = 4
    TAG_INDEX = 5

    def __init__(self, monitor_logcat_cmd, flush_logcat_cmd, device):
        super().__init__()
        self.monitor_logcat_cmd = monitor_logcat_cmd
        self.flush_logcat_cmd = flush_logcat_cmd

        self.device = device
        self.TAG = self.TAG.replace("device_adb_name", device.adb_name)

        self.logs = list()
        self.process = None

    def run(self):
        ShellHelper.execute_shell(self.flush_logcat_cmd, False, False)
        with subprocess.Popen(self.monitor_logcat_cmd, shell=True, stdout=subprocess.PIPE, bufsize=1,
                              universal_newlines=True, errors="replace") as p:
            self.process = p

            current_log = None
            current_process_pid = None

            for line in p.stdout:
                line_cleaned = line.strip()
                line_parts = line_cleaned.split()

                if len(line_parts) <= 5:
                    continue

                if self.TEST_STARTED in line and current_log is None and current_process_pid is None:
                    current_log = TestLogCat()

                    current_process_pid = line_parts[self.PID_INDEX]

                    test_name = re.findall("TestRunner: started:(.+)\(", line_cleaned)
                    current_log.test_name = test_name[0]

                    full_test_package = re.findall("\((.+)\)", line_cleaned)
                    package_parts = full_test_package[0].split(".")
                    current_log.test_container = package_parts.pop().strip()
                    current_log.test_full_package = full_test_package[0].strip() + "." + test_name[0].strip()

                if current_log is not None:
                    if line_parts[self.PID_INDEX] == current_process_pid:
                        logcat_line = TestLogCatLine()

                        date = line_parts[self.DATE_INDEX]
                        logcat_line.date = date

                        time_hour = line_parts[self.TIME_INDEX]
                        logcat_line.time = time_hour

                        level = line_parts[self.LEVEL_INDEX]
                        logcat_line.level = level

                        tag = line_parts[self.TAG_INDEX]
                        if len(tag) > 0 and tag[len(tag) - 1] == ":":
                            tag = tag[:-1]
                        logcat_line.tag = tag

                        string_pos = line_cleaned.find(tag)
                        length_tag = len(tag)
                        text = line_cleaned[(string_pos + length_tag):].strip()
                        if text.startswith(":"):
                            text = text[1:]
                            text = text.strip()
                        logcat_line.text = text

                        current_log.lines.append(logcat_line)

                if self.TEST_FINISHED in line:
                    self.logs.append(current_log)
                    current_log = None
                    current_process_pid = None

    def kill_logcat_monitoring(self):
        self.process.kill()


class TestThread(threading.Thread):
    TAG = "TestThread<device_adb_name>:"

    TEST_ENDED_WITH_SUCCESS_0 = "INSTRUMENTATION_STATUS_CODE: 0"
    TEST_ENDED_WITH_FAILURE = "INSTRUMENTATION_STATUS_CODE: -2"

    TEST_NAME = "INSTRUMENTATION_STATUS: test="
    TEST_PACKAGE = "INSTRUMENTATION_STATUS: class="
    TEST_OUTPUT_STACK_STARTED = "INSTRUMENTATION_STATUS: stack="
    TEST_CURRENT_TEST_NUMBER = "INSTRUMENTATION_STATUS: current"

    def __init__(self, launch_tests_cmd, device):
        super().__init__()
        self.launch_tests_cmd = launch_tests_cmd

        self.device = device
        self.TAG = self.TAG.replace("device_adb_name", device.adb_name)

        self.logs = list()
        self.is_finished = False

    def run(self):
        try:
            Printer.console_highlighted(self.TAG, "Executing shell command: ", self.launch_tests_cmd)
            with subprocess.Popen(self.launch_tests_cmd, shell=True, stdout=subprocess.PIPE, bufsize=1,
                                  universal_newlines=True) as p:

                reading_stack_in_progress = False
                current_log = None
                stack = None
                for line in p.stdout:
                    if self.TEST_NAME in line and current_log is None:
                        current_log = TestSummary()
                        current_log.test_name = line.replace(self.TEST_NAME, "").strip()
                        current_log.test_start_time = int(round(time.time() * 1000))
                        current_log.device = self.device.adb_name

                        Printer.console(self.TAG + " Test '" + current_log.test_name + "'\n", end='')

                    if self.TEST_PACKAGE in line:
                        line = line.replace(self.TEST_PACKAGE, "").strip()
                        package_parts = line.split(".")
                        current_log.test_container = package_parts.pop()
                        current_log.test_full_package = line + "." + current_log.test_name

                    if self.TEST_OUTPUT_STACK_STARTED in line:
                        stack = ""
                        reading_stack_in_progress = True

                    if self.TEST_CURRENT_TEST_NUMBER in line:
                        if stack is not None:
                            current_log.error_messages.append(stack)
                        reading_stack_in_progress = False
                        stack = None

                    if self.TEST_ENDED_WITH_SUCCESS_0 in line:
                        current_log.test_end_time = int(round(time.time() * 1000))
                        current_log.test_status = "success"
                        self.logs.append(current_log)
                        current_log = None

                    if self.TEST_ENDED_WITH_FAILURE in line:
                        current_log.test_end_time = int(round(time.time() * 1000))
                        current_log.test_status = "failure"
                        self.logs.append(current_log)
                        current_log = None

                    if reading_stack_in_progress:
                        if self.TEST_OUTPUT_STACK_STARTED in line:
                            test_error_info = self.TAG + " Test '" + current_log.test_name + "' - FAILED\n"
                            Printer.console(test_error_info, end="")
                            line = line.replace(self.TEST_OUTPUT_STACK_STARTED, "")
                        stack += line
                        Printer.console(line, end="")

            if p.returncode != 0:
                message = str(p.returncode) + " : " + str(p.args)
                raise LauncherFlowInterruptedException(self.TAG, message)
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
