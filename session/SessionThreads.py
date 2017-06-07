import time
import re
import os
import subprocess
import threading

from error.Exceptions import LauncherFlowInterruptedException

from settings import GlobalConfig

from session.SessionModels import (
    TestLogCat,
    TestLogCatLine,
    TestSummary
)

from system.file import FileUtils
from system.console import ShellHelper
from system.console import (
    Printer,
    Color
)


class TestSummarySavingThread(threading.Thread):
    TAG = "TestSummarySavingThread"

    TEST_SUMMARY_APPENDIX = "test_summary.json"

    def __init__(self, device, test_summary_list):
        super().__init__()
        self.device = device
        self.test_summary_list = test_summary_list
        self.created_files = None

    def run(self):
        self.created_files = list()

        for test_summary in self.test_summary_list:
            test_summary_json_dict = vars(test_summary)
            created_file_path = FileUtils.save_json_dict_to_json(GlobalConfig.OUTPUT_TEST_LOG_DIR,
                                                                 test_summary_json_dict,
                                                                 test_summary_json_dict["test_name"]
                                                                 + "_" + self.device.adb_name
                                                                 + "_" + self.TEST_SUMMARY_APPENDIX)
            self.created_files.append(created_file_path)

    def is_finished(self):
        return self.created_files is not None and len(self.created_files) == len(self.test_summary_list) \
               and all(os.path.isfile(file) for file in self.created_files)


class TestLogcatSavingThread(threading.Thread):
    TAG = "TestLogcatSavingThread"

    TEST_LOGCAT_APPENDIX = "logcat.json"

    def __init__(self, device, test_logcat_list):
        super().__init__()
        self.device = device
        self.test_logcat_list = test_logcat_list
        self.created_files = None

    def run(self):
        self.created_files = list()

        for logcat in self.test_logcat_list:
            logcat_lines_json_dict = list()
            for logcat_line in logcat.lines:
                logcat_lines_json_dict.append(vars(logcat_line))
            logcat.lines = logcat_lines_json_dict

            logcat_json_dict = vars(logcat)
            created_file_path = FileUtils.save_json_dict_to_json(GlobalConfig.OUTPUT_TEST_LOGCAT_DIR,
                                                                 logcat_json_dict,
                                                                 logcat_json_dict["test_name"]
                                                                 + "_" + self.device.adb_name
                                                                 + "_" + self.TEST_LOGCAT_APPENDIX)
            self.created_files.append(created_file_path)

    def is_finished(self):
        return self.created_files is not None and len(self.created_files) == len(self.test_logcat_list) \
               and all(os.path.isfile(file) for file in self.created_files)


class TestRecordingSavingThread(threading.Thread):
    TAG = "TestRecordingSavingThread"

    def __init__(self, device):
        super().__init__()
        self.device = device

        self.recordings = list()
        self.recording_pull_cmds = dict()
        self.recording_clear_cmds = dict()

        self.should_finish = False

    def run(self):
        while True:
            if self.recordings and self._all_recordings_has_commands():
                recording = self.recordings.pop()

                time.sleep(10)
                ShellHelper.execute_shell(self.recording_pull_cmds.get(recording), False, False)
                ShellHelper.execute_shell(self.recording_clear_cmds.get(recording), False, False)

            if self.should_finish:
                break

    def _all_recordings_has_commands(self):
        all_recordings_have_commands = True
        for recording in self.recordings:
            pull_cmd = self.recording_pull_cmds.get(recording)
            remove_cmd = self.recording_clear_cmds.get(recording)

            if pull_cmd is None or remove_cmd is None:
                all_recordings_have_commands = False
                break

        return all_recordings_have_commands

    def add_recordings(self, recording_list):
        self.recordings.extend(recording_list)

    def add_pull_recording_cmds(self, pull_recording_cmds):
        for cmd in pull_recording_cmds:
            for recording_name in self.recordings:
                if recording_name in cmd:
                    self.recording_pull_cmds.update({recording_name: cmd})

    def add_clear_recordings_cmd(self, clear_recording_cmds):
        for cmd in clear_recording_cmds:
            for recording_name in self.recordings:
                if recording_name in cmd:
                    self.recording_clear_cmds.update({recording_name: cmd})

    def kill_processes(self):
        self.should_finish = True


class TestRecordingThread(threading.Thread):
    TAG = "TestRecordingThread<device_adb_name>:"

    def __init__(self, start_recording_cmd, recording_name, device):
        super().__init__()
        self.start_recording_cmd = start_recording_cmd
        self.recording_name = recording_name

        self.device = device
        self.TAG = self.TAG.replace("device_adb_name", device.adb_name)

        self.device = list()
        self.process = None

    def run(self):
        with subprocess.Popen(self.start_recording_cmd + self.recording_name, shell=True, stdout=subprocess.PIPE,
                              bufsize=1, universal_newlines=True) as p:
            self.process = p

    def kill_processes(self):
        if self.process is not None and hasattr(self.process, "kill"):
            self.process.kill()


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

    def __init__(self, device, device_commands_dict, should_record_screen):
        super().__init__()
        self.monitor_logcat_cmd = device_commands_dict["monitor_logcat_cmd"]
        self.flush_logcat_cmd = device_commands_dict["flush_logcat_cmd"]
        self.record_screen_cmd = device_commands_dict["record_screen_cmd"]

        self.device = device
        self.TAG = self.TAG.replace("device_adb_name", device.adb_name)
        self.should_record_screen = should_record_screen

        self.logs = list()
        self.recordings = list()

        self.logcat_process = None
        self.screen_recording_thread = None

    def run(self):
        with subprocess.Popen(self.monitor_logcat_cmd, shell=True, stdout=subprocess.PIPE, bufsize=1,
                              universal_newlines=True, errors="replace") as p:
            self.logcat_process = p

            current_log = None
            current_process_pid = None
            current_recording_name = None

            for line in p.stdout:
                line_cleaned = line.strip()
                line_parts = line_cleaned.split()

                if len(line_parts) <= 5:
                    continue

                if self.TEST_STARTED in line and current_log is None and current_process_pid is None:
                    current_log = TestLogCat()

                    current_process_pid = line_parts[self.PID_INDEX]

                    test_name = re.findall("TestRunner: started:(.+)\(", line_cleaned)
                    current_log.test_name = test_name[0].strip()

                    full_test_package = re.findall("\((.+)\)", line_cleaned)
                    package_parts = full_test_package[0].split(".")
                    current_log.test_container = package_parts.pop().strip()
                    current_log.test_full_package = full_test_package[0].strip() + "." + test_name[0].strip()
                    if self.should_record_screen:
                        self._restart_recording(current_log.test_name)
                        if current_recording_name is not None:
                            self.recordings.append(current_recording_name)
                        current_recording_name = self.screen_recording_thread.recording_name

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

                    if self.should_record_screen:
                        self._stop_recording()
                        self.recordings.append(current_recording_name)

                    current_log = None
                    current_process_pid = None
                    current_recording_name = None

                    ShellHelper.execute_shell(self.flush_logcat_cmd, False, False)

    def _stop_recording(self):
        if self.screen_recording_thread is not None:
            self.screen_recording_thread.kill_processes()
            self.screen_recording_thread = None

    def _restart_recording(self, test_name):
        if self.screen_recording_thread is None or not self.screen_recording_thread.is_alive():
            recording_name = test_name + "-" + str(int(round(time.time() * 1000))) + ".mp4"
            self.screen_recording_thread = TestRecordingThread(self.record_screen_cmd, recording_name, self.device)
            self.screen_recording_thread.start()

    def kill_processes(self):
        if self.screen_recording_thread is not None:
            self.screen_recording_thread.kill_processes()

        if self.logcat_process is not None and hasattr(self.logcat_process, "kill"):
            self.logcat_process.kill()


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

        self.test_process = None

    def run(self):
        Printer.console_highlighted(self.TAG, "Executing shell command: ", self.launch_tests_cmd)
        with subprocess.Popen(self.launch_tests_cmd, shell=True, stdout=subprocess.PIPE, bufsize=1,
                              universal_newlines=True) as p:
            self.test_process = p

            reading_stack_in_progress = False
            current_log = None
            stack = None

            for line in p.stdout:
                if self.TEST_NAME in line and current_log is None:
                    current_log = TestSummary()
                    current_log.test_name = line.replace(self.TEST_NAME, "").strip()
                    current_log.test_start_time = int(round(time.time() * 1000))
                    current_log.device = self.device.adb_name

                    Printer.console(self.TAG + " Test " + current_log.test_name + "\n", end='')

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
                        test_error_info = self.TAG + " Test " + current_log.test_name + " - FAILED\n"
                        Printer.console(test_error_info, end="")
                        line = line.replace(self.TEST_OUTPUT_STACK_STARTED, "")
                    stack += line
                    Printer.console(line, end="")

    def kill_processes(self):
        if self.test_process is not None and hasattr(self.test_process, "kill"):
            self.test_process.kill()


class ApkInstallThread(threading.Thread):
    TAG = "ApkInstallThread<device_adb_name>:"

    def __init__(self, dump_badging_cmd, device, apk_name, apk_path):
        super().__init__()
        self.dump_badging_cmd = dump_badging_cmd

        self.device = device
        self.TAG = self.TAG.replace("device_adb_name", device.adb_name)

        self.apk_name = apk_name
        self.apk_path = apk_path

        self.install_time = 0
        self.note = None
        self.is_finished = False

    def run(self):
        start_time = int(round(time.time() * 1000))

        package = self._get_apk_package()
        installed_packages_str = self.device.get_installed_packages()

        if package in installed_packages_str:
            Printer.system_message(self.TAG, "Package " + Color.GREEN + package + Color.BLUE +
                                   " is currently installed on device '" + Color.GREEN + self.device.adb_name
                                   + Color.BLUE + ". Removing from device...")
            self.device.uninstall_package(package)
        else:
            Printer.system_message(self.TAG, "Package " + Color.GREEN + package + Color.BLUE +
                                   " was not found on device '" + Color.GREEN + self.device.adb_name + Color.BLUE + ".")

        Printer.system_message(self.TAG, "Installing .*apk file...")
        self.device.install_apk(self.apk_path)

        end_time = int(round(time.time() * 1000))
        self.install_time = (end_time - start_time) / 1000

        Printer.system_message(self.TAG, ".*apk " + Color.GREEN + self.apk_path + Color.BLUE
                               + " was successfully installed on device " + Color.GREEN + self.device.adb_name
                               + Color.BLUE + ". It took " + Color.GREEN + str(self.install_time) + Color.BLUE
                               + " seconds.")
        self.is_finished = True

    def _get_apk_package(self):
        dump = ShellHelper.execute_shell(self.dump_badging_cmd, False, False)
        regex_result = re.findall("package: name='(.+?)'", dump)
        if regex_result:
            package = str(regex_result[0])
            Printer.system_message(self.TAG, "Package that is about to be installed: " + Color.GREEN + package
                                   + Color.BLUE + ".")
        else:
            message = "Unable to find package of .*apk file: " + self.apk_name
            raise LauncherFlowInterruptedException(self.TAG, message)
        return package
