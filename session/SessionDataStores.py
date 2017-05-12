import copy
import re
import os
import glob

from settings import GlobalConfig

from session.SessionModels import (
    OutsideSessionVirtualDevice,
    OutsideSessionDevice,
    SessionVirtualDevice,
    ApkCandidate,
    TestLogCatWrapper,
    TestLogCatPackage,
    TestSummaryWrapper,
    TestSummaryPackage
)

from system.file import FileUtils
from system.port import PortManager
from system.console import (
    Printer,
    Color
)


class ApkStore:
    TAG = "ApkStore:"

    def __init__(self, aapt_controller):
        self.aapt_controller = aapt_controller
        self.apk_candidates = list()
        self._create_apk_dir_if_not_exists()

    def _create_apk_dir_if_not_exists(self):
        if os.path.isdir(GlobalConfig.APK_DIR):
            Printer.system_message(self.TAG, "Directory " + Color.GREEN + GlobalConfig.APK_DIR + Color.BLUE
                                   + " was found.")
        else:
            Printer.system_message(self.TAG, "Directory " + Color.GREEN + GlobalConfig.APK_DIR + Color.BLUE
                                   + " not found. Creating...")
            FileUtils.create_dir(GlobalConfig.APK_DIR)

    def provide_apk(self, test_set):
        self._find_candidates(test_set)
        self._display_candidates()
        return self._get_usable_apk_candidate_for_latest_version()

    def _find_candidates(self, test_set):
        name_part = test_set.apk_name_part.replace(".apk", "")
        Printer.system_message(self.TAG,
                               "Checking " + Color.GREEN + GlobalConfig.APK_DIR + Color.BLUE + " directory for .*apk" +
                               " list with names containing " + Color.GREEN + name_part + Color.BLUE + ":")

        app_apk_list = self.get_list_with_application_apk(name_part, GlobalConfig.APK_DIR)
        app_apk_filepath_list = self.get_list_with_application_apk_filepath(name_part, GlobalConfig.APK_DIR)
        test_apk_list = self.get_list_with_test_apk(name_part, GlobalConfig.APK_DIR)
        test_apk_filepath_list = self.get_list_with_test_apk_filepath(name_part, GlobalConfig.APK_DIR)

        for apk in app_apk_list:
            apk_filename = apk
            apk_filename_without_extension = apk_filename.replace(".apk", "")

            apk_filepath = ""
            for path in app_apk_filepath_list:
                if apk_filename_without_extension and "-androidTest" not in path:
                    apk_filepath = path

            version_code = -1
            if apk_filepath is not None:
                dump = self.aapt_controller.dump_badging(apk_filepath)
                version_code = re.findall("versionCode='(.+?)'", dump)
                version_code = int(version_code[0])

            apk_test_filename = ""
            for apk_name in test_apk_list:
                if apk_filename_without_extension in apk_name and "-androidTest" in apk_name:
                    apk_test_filename = apk_name

            apk_test_filepath = ""
            for path in test_apk_filepath_list:
                if apk_filename_without_extension in path and "-androidTest" in path:
                    apk_test_filepath = path

            self.apk_candidates.append(ApkCandidate(apk_filename,
                                                    apk_filepath,
                                                    apk_test_filename,
                                                    apk_test_filepath,
                                                    version_code))

    def _display_candidates(self):
        candidate_no = 0
        for apk_info in self.apk_candidates:
            candidate_no += 1
            Printer.system_message(self.TAG, "- Candidate no." + str(candidate_no) + " "
                                   + (Color.GREEN + "('can be used in test')" if apk_info.is_usable()
                                      else Color.RED + "('cannot be used in test - missing fields')"))
            Printer.system_message(self.TAG,
                                   "  Apk candidate name: " + Color.GREEN + str(apk_info.apk_name) + Color.END)
            Printer.system_message(self.TAG,
                                   "  Apk candidate path: " + Color.GREEN + str(apk_info.apk_path) + Color.END)
            Printer.system_message(self.TAG,
                                   "  Related test apk: " + Color.GREEN + str(apk_info.test_apk_name) + Color.END)
            Printer.system_message(self.TAG, "  Related test apk path: " + Color.GREEN + str(apk_info.test_apk_path)
                                   + Color.END)
            Printer.system_message(self.TAG, "  Version: " + Color.GREEN + str(apk_info.apk_version) + Color.END)

    def _get_usable_apk_candidate_for_latest_version(self):
        latest_apk_info = None
        latest_ver = -1
        for apk_info in self.apk_candidates:
            if apk_info.is_usable() and apk_info.apk_version > latest_ver:
                latest_apk_info = apk_info
                latest_ver = apk_info.apk_version
        return latest_apk_info

    @staticmethod
    def get_list_with_application_apk(apk_name_part_cleaned, apk_dir):
        apk_filenames = os.listdir(apk_dir)

        application_apk_list = list()
        for apk_filename in apk_filenames:
            if apk_name_part_cleaned in apk_filename and "androidTest" not in apk_filename:
                application_apk_list.append(apk_filename)
        return application_apk_list

    @staticmethod
    def get_list_with_application_apk_filepath(apk_name_part_cleaned, apk_dir):
        apk_absolute_paths = glob.glob(apk_dir + "*")

        application_apk_filepath_list = list()
        for apk_path in apk_absolute_paths:
            if apk_name_part_cleaned in apk_path and "androidTest" not in apk_path:
                application_apk_filepath_list.append(apk_path)
        return application_apk_filepath_list

    @staticmethod
    def get_list_with_test_apk(apk_name_part_cleaned, apk_dir):
        apk_filenames = os.listdir(apk_dir)

        test_apk_list = list()
        for apk_filename in apk_filenames:
            if apk_name_part_cleaned in apk_filename and "androidTest" in apk_filename:
                test_apk_list.append(apk_filename)
        return test_apk_list

    @staticmethod
    def get_list_with_test_apk_filepath(apk_name_part_cleaned, apk_dir):
        apk_absolute_paths = glob.glob(apk_dir + "*")

        application_apk_filepath_list = list()
        for apk_path in apk_absolute_paths:
            if apk_name_part_cleaned in apk_path and "androidTest" in apk_path:
                application_apk_filepath_list.append(apk_path)
        return application_apk_filepath_list


class DeviceStore:
    TAG = "DeviceStore:"

    def __init__(self,
                 adb_controller,
                 adb_package_manager_controller,
                 adb_settings_controller,
                 avdmanager_controller,
                 emulator_controller):

        self.adb_controller = adb_controller
        self.adb_package_manager_controller = adb_package_manager_controller
        self.adb_settings_controller = adb_settings_controller
        self.avdmanager_controller = avdmanager_controller
        self.emulator_controller = emulator_controller

        self.outside_session_virtual_devices = list()
        self.outside_session_devices = list()
        self.session_devices = list()

    def prepare_outside_session_devices(self):
        currently_visible_devices = self._get_visible_devices()

        for device_name, status in currently_visible_devices.items():
            if "emulator" not in device_name:
                outside_session_device = OutsideSessionDevice(device_name,
                                                              status,
                                                              self.adb_controller,
                                                              self.adb_package_manager_controller,
                                                              self.adb_settings_controller)
                Printer.system_message(self.TAG, "Android Device model representing device with name "
                                       + Color.GREEN + device_name + Color.BLUE + " was added to test run.")
                self.outside_session_devices.append(outside_session_device)

        if not any(isinstance(device, OutsideSessionDevice) for device in self.outside_session_devices):
            Printer.system_message(self.TAG, "No Android Devices connected to PC were found.")

    def prepare_outside_session_virtual_devices(self):
        currently_visible_devices = self._get_visible_devices()

        for device_name, status in currently_visible_devices.items():
            if "emulator" in device_name:
                outside_session_virtual_device = OutsideSessionVirtualDevice(device_name,
                                                                             status,
                                                                             self.adb_controller,
                                                                             self.adb_package_manager_controller,
                                                                             self.adb_settings_controller)
                Printer.system_message(self.TAG, "AVD model representing device with name "
                                       + Color.GREEN + device_name + Color.BLUE + " was added to test run.")
                self.outside_session_virtual_devices.append(outside_session_virtual_device)

        if not any(isinstance(device, OutsideSessionVirtualDevice) for device in self.outside_session_virtual_devices):
            Printer.system_message(self.TAG, "No currently launched AVD were found.")

    def prepare_session_devices(self, avd_set, avd_schemas):
        avd_ports = PortManager.get_open_ports(avd_set)
        for avd in avd_set.avd_list:
            instances_of_schema = avd.instances
            for i in range(instances_of_schema):
                avd_schema = copy.deepcopy(avd_schemas[avd.avd_name])
                avd_schema.avd_name = avd_schema.avd_name + "-" + str(i)
                port = avd_ports.pop(0)
                log_file = FileUtils.create_output_file(avd_schema.avd_name, "txt")

                session_device = SessionVirtualDevice(avd_schema,
                                                      port,
                                                      log_file,
                                                      self.avdmanager_controller,
                                                      self.emulator_controller,
                                                      self.adb_controller,
                                                      self.adb_package_manager_controller,
                                                      self.adb_settings_controller)
                self.session_devices.append(session_device)
                Printer.system_message(self.TAG, "Android Virtual Device model was created according to schema "
                                       + Color.GREEN + avd_schema.avd_name + Color.BLUE +
                                       ". Instance number: " + str(i) + ". Assigned to port: " + str(port) + ".")

    def _get_visible_devices(self):
        currently_visible_devices = dict()
        adb_devices_output = self.adb_controller.devices()

        for line in adb_devices_output.splitlines():
            device_name = line.split()[0]
            device_status = line.split()[1]

            # edge case
            if device_name == "*":
                continue

            currently_visible_devices.update({device_name: device_status})

        return currently_visible_devices

    def get_devices(self):
        return self.session_devices + self.outside_session_devices + self.outside_session_virtual_devices

    def update_model_statuses(self):
        currently_visible_devices = self._get_visible_devices()

        for session_device in self.session_devices:
            session_device.status = "not-launched"

        for outside_session_device in self.outside_session_devices:
            outside_session_device.status = "not-launched"

        for outside_session_virtual_device in self.outside_session_virtual_devices:
            outside_session_virtual_device.status = "not-launched"

        for device_name, status in currently_visible_devices.items():
            for session_device in self.session_devices:
                if session_device.adb_name == device_name:
                    session_device.status = status

            for outside_session_device in self.outside_session_devices:
                if outside_session_device.adb_name == device_name:
                    outside_session_device.status = status

            for outside_session_virtual_device in self.outside_session_virtual_devices:
                if outside_session_virtual_device.adb_name == device_name:
                    outside_session_virtual_device.status = status

    def clear_outside_session_virtual_device_models(self):
        self.outside_session_virtual_devices.clear()

    def clear_outside_session_device_models(self):
        self.outside_session_devices.clear()

    def clear_session_avd_models(self):
        self.session_devices.clear()

    def remove_device_from_session(self, device):
        if device in self.outside_session_virtual_devices:
            self.outside_session_virtual_devices.remove(device)
        elif device in self.outside_session_devices:
            self.outside_session_devices.remove(device)
        elif device in self.session_devices:
            self.session_devices.remove(device)
        Printer.system_message(self.TAG, "Device with name "
                               + Color.GREEN + device.adb_name + Color.BLUE + " was removed from session.")


class TestStore:
    TAG = "TestStore:"

    def __init__(self):
        self.packages_to_run = list()

    def get_packages(self, test_set, test_list):
        for package_name in test_set.set_package_names:
            for test_package in test_list[package_name].test_packages:
                if test_package not in self.packages_to_run:
                    self.packages_to_run.append(test_package)


class LogStore:
    TAG = "LogStore:"

    def __init__(self):
        self.test_log_summaries = list()
        self.test_logcats = list()

    def get_test_log_summary_wrapper(self):
        log_summary_wrapper_dict = dict()

        for test_log in self.test_log_summaries:
            full_package = test_log.test_full_package
            package_parts = full_package.split(".")
            package = ".".join(package_parts[:-2])

            test_summary_package = log_summary_wrapper_dict.get(package, TestSummaryPackage())
            test_summary_package.test_package = package
            test_summary_package.test_summaries.append(test_log)
            log_summary_wrapper_dict.update({package: test_summary_package})

        test_summary_wrapper = TestSummaryWrapper()
        test_summary_wrapper.test_summary_packages.extend(list(log_summary_wrapper_dict.values()))
        return test_summary_wrapper

    def get_test_logcat_wrapper(self):
        logcat_wrapper_dict = dict()

        for test_log_cat in self.test_logcats:
            full_package = test_log_cat.test_full_package
            package_parts = full_package.split(".")
            package = ".".join(package_parts[:-2])

            test_logcat_package = logcat_wrapper_dict.get(package, TestLogCatPackage())
            test_logcat_package.test_package = package
            test_logcat_package.test_logcats.append(test_log_cat)
            logcat_wrapper_dict.update({package: test_logcat_package})

        logcat_wrapper = TestLogCatWrapper()
        logcat_wrapper.test_logcat_packages.extend(list(logcat_wrapper_dict.values()))
        return logcat_wrapper

    def get_test_log_summary_wrapper_json_dict(self):
        return self.test_summary_wrapper_to_json_dict(self.get_test_log_summary_wrapper())

    def get_test_logcat_wrapper_json_dict(self):
        return self.test_logcats_wrapper_to_json_dict(self.get_test_logcat_wrapper())

    @staticmethod
    def test_summary_wrapper_to_json_dict(test_summary_wrapper):
        summary_packages_var = list()
        for summary_package in test_summary_wrapper.test_summary_packages:
            summaries_var = list()
            for test_summary in summary_package.test_summaries:
                summaries_var.append(vars(test_summary))
            summary_package.test_summaries = summaries_var
            summary_packages_var.append(vars(summary_package))
        temp_summary_wrapper = TestSummaryWrapper()
        temp_summary_wrapper.test_summary_packages = summary_packages_var
        return vars(temp_summary_wrapper)

    @staticmethod
    def test_logcats_wrapper_to_json_dict(test_logcat_wrapper):
        logcat_packages_var = list()
        for logcat_package in test_logcat_wrapper.test_logcat_packages:
            logcats_var = list()
            for logcat in logcat_package.test_logcats:
                logcat_lines_var = list()
                for logcat_line in logcat.lines:
                    logcat_lines_var.append(vars(logcat_line))
                logcat.lines = logcat_lines_var
                logcats_var.append(vars(logcat))
            logcat_package.test_logcats = logcats_var
            logcat_packages_var.append(vars(logcat_package))
        temp_test_logcat_wrapper = TestLogCatWrapper()
        temp_test_logcat_wrapper.test_logcat_packages = logcat_packages_var
        return vars(temp_test_logcat_wrapper)
