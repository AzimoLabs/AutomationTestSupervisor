import re
import time
import copy

from error.Exceptions import LauncherFlowInterruptedException

from settings import GlobalConfig

from session import SessionGlobalLogger as session_logger
from session.SessionModels import (
    OutsideSessionVirtualDevice,
    SessionVirtualDevice,
)
from session.SessionThreads import (
    TestThread,
    TestSummarySavingThread,
    TestRecordingSavingThread,
    TestLogCatMonitorThread,
    TestLogcatSavingThread,
    ApkInstallThread
)

from system.file import (
    FileUtils
)
from system.console import (
    Printer,
    Color
)


class CleanUpManager:
    TAG = "CleanUpManager"

    def __init__(self, device_store, adb_controller, adb_shell_controller):
        self.device_store = device_store
        self.adb_controller = adb_controller
        self.adb_shell_controller = adb_shell_controller

    def prepare_output_directories(self):
        for directory in [GlobalConfig.OUTPUT_DIR,
                          GlobalConfig.OUTPUT_AVD_LOG_DIR,
                          GlobalConfig.OUTPUT_TEST_LOG_DIR,
                          GlobalConfig.OUTPUT_TEST_LOGCAT_DIR,
                          GlobalConfig.OUTPUT_TEST_RECORDINGS_DIR]:

            if FileUtils.dir_exists(directory):
                Printer.system_message(self.TAG, "Directory " + Color.GREEN + directory + Color.BLUE
                                       + " was found. Removing all files in directory...")
                FileUtils.clear_dir(directory)
            else:
                Printer.system_message(self.TAG, "Directory " + Color.GREEN + directory + Color.BLUE
                                       + " not found. Creating...")
                FileUtils.create_dir(directory)

    def restart_adb(self):
        self.adb_controller.kill_server()
        self.adb_controller.start_server()

    def prepare_device_directories(self):
        for device in self.device_store.get_devices():
            Printer.system_message(self.TAG, "Attempting to re-create " + Color.GREEN
                                   + GlobalConfig.DEVICE_VIDEO_STORAGE_DIR + Color.BLUE + " directory on device "
                                   + Color.GREEN + device.adb_name + Color.BLUE + ".")
            self.adb_shell_controller.remove_files_in_dir(device.adb_name, GlobalConfig.DEVICE_VIDEO_STORAGE_DIR)
            self.adb_shell_controller.create_dir(device.adb_name, GlobalConfig.DEVICE_VIDEO_STORAGE_DIR)


class DeviceManager:
    TAG = "DeviceManager:"

    def __init__(self, device_store, adb_controller, adb_shell_controller, avdmanager_controller):
        self.device_store = device_store
        self.adb_controller = adb_controller
        self.adb_shell_controller = adb_shell_controller
        self.avdmanager_controller = avdmanager_controller

    def add_models_based_on_avd_schema(self, avd_set, avd_schemas):
        self.device_store.prepare_session_devices(avd_set, avd_schemas)

    def add_models_representing_outside_session_devices(self):
        self.device_store.prepare_outside_session_devices()

    def add_models_representing_outside_session_virtual_devices(self):
        self.device_store.prepare_outside_session_virtual_devices()

    def clear_models_based_on_avd_schema(self):
        Printer.system_message(self.TAG, "Clearing all AVD models related to AVD set.")
        self.device_store.clear_session_avd_models()

    def clear_models_representing_outside_session_devices(self):
        Printer.system_message(self.TAG, "Clearing all Android device models.")
        self.device_store.prepare_outside_session_devices()

    def clear_models_representing_outside_session_virtual_devices(self):
        Printer.system_message(self.TAG, "Clearing all AVD models unrelated to AVD set.")
        self.device_store.clear_outside_session_virtual_device_models()

    def clear_models_with_android_ids_in_ignore_list(self):
        for device in self.device_store.get_devices():
            if device.get_android_id() in GlobalConfig.IGNORED_DEVICE_LIST:
                Printer.system_message(self.TAG, "Android-ID "
                                       + Color.GREEN + device.android_id + Color.BLUE +
                                       " of device " + Color.GREEN + device.adb_name + Color.BLUE +
                                       " was found in ignore list.")
                self.device_store.remove_device_from_session(device)
            else:
                Printer.system_message(self.TAG, "Android-ID "
                                       + Color.GREEN + device.android_id + Color.BLUE +
                                       " of device " + Color.GREEN + device.adb_name + Color.BLUE +
                                       " is allowed to run in session.")

    def create_all_avd_and_reuse_existing(self):
        created_avd_list = re.findall("Name: (.+)", self.avdmanager_controller.list_avd())

        for device in self.device_store.get_devices():
            if isinstance(device, SessionVirtualDevice):

                session_logger.log_device_creation_start_time(device.adb_name)
                start_time = int(round(time.time() * 1000))
                if device.avd_schema.avd_name in created_avd_list:
                    Printer.system_message(self.TAG, "AVD with name " + Color.GREEN + str(device.avd_schema.avd_name)
                                           + Color.BLUE + " currently exists and will be reused.")
                else:
                    device.create()

                if device.avd_schema.create_avd_hardware_config_filepath != "":
                    Printer.system_message(self.TAG,
                                           "'config.ini' file was specified in AVD schema of device " + Color.GREEN
                                           + device.adb_name + Color.BLUE + " in location " + Color.GREEN
                                           + device.avd_schema.create_avd_hardware_config_filepath + Color.BLUE
                                           + ". Applying...")
                    device.apply_config_ini()
                end_time = int(round(time.time() * 1000))
                session_logger.log_device_creation_end_time(device.adb_name)

                creation_time = (end_time - start_time) / 1000
                reasonable_time = 25
                if creation_time > reasonable_time and "--force" not in device.avd_schema.create_avd_additional_options:
                    Printer.system_message(self.TAG, "AVD creation took: " + Color.GREEN + str(creation_time) + " sec"
                                           + Color.RED + " (Attention! Creation process could ran faster. Try adding "
                                           + "'--force' to your AVD schema in 'create_avd_additional_options' field.)")
                else:
                    Printer.system_message(self.TAG, "AVD creation took: " + Color.GREEN + str(creation_time)
                                           + Color.BLUE + " seconds.")

    def create_all_avd_and_recreate_existing(self):
        created_avd_list = re.findall("Name: (.+)", self.avdmanager_controller.list_avd())

        for device in self.device_store.get_devices():
            if isinstance(device, SessionVirtualDevice):

                session_logger.log_device_creation_start_time(device.adb_name)
                start_time = int(round(time.time() * 1000))
                if device.avd_schema.avd_name in created_avd_list:
                    Printer.system_message(self.TAG, "AVD with name " + Color.GREEN + device.avd_schema.avd_name
                                           + Color.BLUE + " already exists and will be re-created.")
                    device.delete()
                    device.create()
                else:
                    device.create()

                if device.avd_schema.create_avd_hardware_config_filepath != "":
                    Printer.system_message(self.TAG,
                                           "'config.ini' file was specified in AVD schema of device " + Color.GREEN
                                           + device.adb_name + Color.BLUE + " in location " + Color.GREEN
                                           + device.avd_schema.create_avd_hardware_config_filepath + Color.BLUE
                                           + ". Applying...")
                    device.apply_config_ini()
                end_time = int(round(time.time() * 1000))
                session_logger.log_device_creation_end_time(device.adb_name)

                creation_time = (end_time - start_time) / 1000
                reasonable_time = 25
                if creation_time > reasonable_time and "--force" not in device.avd_schema.create_avd_additional_options:
                    Printer.system_message(self.TAG, "AVD creation took: " + Color.GREEN + str(creation_time) + " sec"
                                           + Color.RED + " (Attention! Creation process could ran faster. Try adding "
                                           + "'--force' to your AVD schema in 'create_avd_additional_options' field.)")
                else:
                    Printer.system_message(self.TAG, "AVD creation took: " + Color.GREEN + str(creation_time)
                                           + Color.BLUE + " sec")

    def launch_all_avd_sequentially(self):
        for device in self.device_store.get_devices():
            if isinstance(device, SessionVirtualDevice) and device.status == "not-launched":
                session_logger.log_device_launch_start_time(device.adb_name)
                device.launch()

            self._wait_for_adb_statuses_change_to("device", (device,))
        self._wait_for_property_statuses(self.device_store.get_devices())

    def launch_all_avd_at_once(self):
        for device in self.device_store.get_devices():
            if isinstance(device, SessionVirtualDevice) and device.status == "not-launched":
                session_logger.log_device_launch_start_time(device.adb_name)
                device.launch()

        self._wait_for_adb_statuses_change_to("device", self.device_store.get_devices())
        self._wait_for_property_statuses(self.device_store.get_devices())

    def _wait_for_adb_statuses_change_to(self, status, monitored_devices):
        Printer.system_message(self.TAG, "Waiting until ("
                               + " ".join("'" + device.adb_name + "'" for device in monitored_devices) +
                               ") devices status will change to '" + status + "'.")

        timeout = GlobalConfig.AVD_ADB_BOOT_TIMEOUT
        start_time = last_scan_ended = time.time() * 1000
        while True:
            current_time = time.time() * 1000

            if current_time - last_scan_ended >= GlobalConfig.ADB_SCAN_INTERVAL or start_time == last_scan_ended:
                Printer.system_message(self.TAG, "Scanning...")

                self.device_store.update_model_statuses()
                Printer.system_message(self.TAG, "  * Current wait status:")
                for device in monitored_devices:
                    Printer.system_message(self.TAG, "    " + device.adb_name + " " + Color.GREEN
                                           + "('" + device.status + "')")

                if all(device.status == status for device in monitored_devices):
                    break

                last_scan_ended = time.time() * 1000

            if current_time - start_time >= timeout:
                message = "Devices took longer than {} seconds to launch (ADB launch). Timeout quit."
                message = message.format(str(timeout))
                raise LauncherFlowInterruptedException(self.TAG, message)

        Printer.system_message(self.TAG, "ADB wait finished with success!")

    def _wait_for_property_statuses(self, monitored_devices):
        Printer.system_message(self.TAG,
                               "Waiting for 'dev.bootcomplete', 'sys.boot_completed', 'init.svc.bootanim', "
                               "properties of devices (" + " ".join(
                                   "'" + device.adb_name + "'" for device in monitored_devices) + ").")

        device_statuses = dict()
        for device in monitored_devices:
            device_statuses.update({device.adb_name: None})

        start_time = last_scan_ended = time.time() * 1000
        while True:
            current_time = time.time() * 1000

            if current_time - last_scan_ended >= GlobalConfig.ADB_SCAN_INTERVAL or start_time == last_scan_ended:
                Printer.system_message(self.TAG, "Scanning...")

                for device in self.device_store.get_devices():
                    if device in monitored_devices:
                        dev_boot = (self.adb_shell_controller
                                    .get_property(device.adb_name, "dev.bootcomplete")).strip()
                        sys_boot = (self.adb_shell_controller
                                    .get_property(device.adb_name, "sys.boot_completed")).strip()
                        boot_anim = (self.adb_shell_controller
                                     .get_property(device.adb_name, "init.svc.bootanim")).strip()

                        boot_finished = dev_boot == "1" and sys_boot == "1" and boot_anim == "stopped"
                        device_statuses.update({device.adb_name: {"dev.bootcomplete": dev_boot,
                                                                  "sys.boot_completed": sys_boot,
                                                                  "init.svc.bootanim": boot_anim,
                                                                  "boot_finished": boot_finished}})
                        if boot_finished:
                            session_logger.log_device_launch_end_time(device.adb_name)

                Printer.system_message(self.TAG, "  * Current wait status:")
                for device_name, status_dict in device_statuses.items():
                    bcplte = str(status_dict["dev.bootcomplete"] if status_dict["dev.bootcomplete"] != "" else "0")
                    bcplted = str(status_dict["sys.boot_completed"] if status_dict["sys.boot_completed"] != "" else "0")
                    banim = str(status_dict["init.svc.bootanim"])
                    launched_status = "launched" if status_dict["boot_finished"] else "not-launched"
                    Printer.system_message(self.TAG, "    " + device_name + " properties: "
                                           + "('dev.bootcomplete' : " + bcplte + ", "
                                           + "'sys.boot_completed' : " + bcplted + ", "
                                           + "'init.svc.bootanim' : " + banim + ") - "
                                           + Color.GREEN + launched_status + Color.BLUE)

                if all(status_dict["boot_finished"] for status_dict in device_statuses.values()):
                    break

                last_scan_ended = time.time() * 1000

            if current_time - start_time >= GlobalConfig.AVD_SYSTEM_BOOT_TIMEOUT:
                message = "Devices took longer than seconds to launch (Property launch). Timeout quit."
                message = message.format(str(GlobalConfig.AVD_SYSTEM_BOOT_TIMEOUT))
                raise LauncherFlowInterruptedException(self.TAG, message)

        Printer.system_message(self.TAG, "Property launch finished with success!")

    def kill_all_avd(self):
        self.device_store.update_model_statuses()
        Printer.system_message(self.TAG, "Currently visible AVD:")

        avd_list = list()
        for device in self.device_store.get_devices():
            if isinstance(device, OutsideSessionVirtualDevice) or isinstance(device, SessionVirtualDevice):
                avd_list.append(device)
                Printer.system_message(self.TAG, "- " + device.adb_name + Color.GREEN + " ('" + device.status + "')"
                                       + Color.BLUE)
                if device.status != "not-launched":
                    device.kill()
                    time.sleep(2)

        self._wait_for_adb_statuses_change_to("not-launched", avd_list)

    def is_any_avd_visible(self):
        self.device_store.update_model_statuses()
        return any("emulator" in device.adb_name for device in self.device_store.get_devices())


class ApkManager:
    TAG = "ApkManager:"

    def __init__(self, device_store, apk_store, gradle_controller, aapt_controller):
        self.device_store = device_store
        self.apk_store = apk_store
        self.gradle_controller = gradle_controller
        self.aapt_controller = aapt_controller

    def display_picked_apk_info(self):
        self.apk_store.display_candidates()
        if self.apk_store.usable_apk_candidate is not None:
            Printer.system_message(self.TAG, "Picked .*apk with highest version code:\n" +
                                   Color.GREEN + str(self.apk_store.usable_apk_candidate) + Color.BLUE + ".")

    def build_apk(self, test_set):
        Printer.system_message(self.TAG, "Building application and test .*apk from scratch.")

        session_logger.log_app_apk_build_start_time()
        self.gradle_controller.build_application_apk(test_set)
        session_logger.log_app_apk_build_end_time()

        session_logger.log_test_apk_build_start_time()
        self.gradle_controller.build_test_apk(test_set)
        session_logger.log_test_apk_build_end_time()

        return self.get_existing_apk(test_set)

    def get_existing_apk(self, test_set):
        apk_candidate = self.apk_store.usable_apk_candidate
        if apk_candidate is None:
            apk_candidate = self.apk_store.provide_apk(test_set)
            if apk_candidate is None:
                message = "No .apk* candidates for test session were found. Check your config. Launcher will quit."
                raise LauncherFlowInterruptedException(self.TAG, message)

        session_logger.log_app_apk(apk_candidate.apk_name)
        session_logger.log_test_apk(apk_candidate.test_apk_name)
        session_logger.log_apk_version_code(apk_candidate.apk_version)

        if session_logger.session_log.apk_summary.apk_build_time is None:
            session_logger.session_log.apk_summary.apk_build_time = 0

        if session_logger.session_log.apk_summary.test_apk_build_time is None:
            session_logger.session_log.apk_summary.test_apk_build_time = 0

        return apk_candidate

    def install_apk_on_devices(self, apk):
        if not self.device_store.get_devices():
            message = "No devices were found in test session. Launcher will quit."
            message = message.format(str(GlobalConfig.AVD_SYSTEM_BOOT_TIMEOUT))
            raise LauncherFlowInterruptedException(self.TAG, message)

        self._install_apk(apk)

    def _install_apk(self, apk):
        aapt_cmd_assembler = self.aapt_controller.aapt_command_assembler

        app_apk_log_note = "appApkThread"
        test_apk_log_note = "testApkThread"

        for device in self.device_store.get_devices():
            if device.status != "device":
                message = (".*apk won't be installed on device with name " + device.adb_name + " because it's ADB "
                           + "status is set to " + device.status + " instead of 'device'.")
                raise LauncherFlowInterruptedException(self.TAG, message)

        apk_install_threads = dict()
        for device in self.device_store.get_devices():
            app_dump_badging_cmd = aapt_cmd_assembler.assemble_dump_badging_cmd(self.aapt_controller.aapt_bin,
                                                                                apk.apk_path)
            app_apk_thread = ApkInstallThread(app_dump_badging_cmd, device, apk.apk_name, apk.apk_path)
            app_apk_thread.note = app_apk_log_note

            test_dump_badging_cmd = aapt_cmd_assembler.assemble_dump_badging_cmd(self.aapt_controller.aapt_bin,
                                                                                 apk.test_apk_path)

            test_apk_thread = ApkInstallThread(test_dump_badging_cmd, device, apk.test_apk_name, apk.test_apk_path)
            test_apk_thread.note = test_apk_log_note

            thread_list = list()
            thread_list.append(app_apk_thread)
            thread_list.append(test_apk_thread)

            apk_install_threads.update({device: thread_list})

        all_devices_have_apk_installed = False
        while not all_devices_have_apk_installed:
            for device in self.device_store.get_devices():
                device_threads = apk_install_threads[device]

                for thread in device_threads:
                    if any(thread.is_alive() for thread in device_threads):
                        break

                    if not thread.is_finished:
                        thread.start()
                        if thread.note == app_apk_log_note:
                            session_logger.log_app_apk_install_start_time_on_device(device.adb_name)
                        if thread.note == test_apk_log_note:
                            session_logger.log_test_apk_install_start_time_on_device(device.adb_name)

            all_threads_has_finished = True
            for device in self.device_store.get_devices():
                device_threads = apk_install_threads[device]

                for thread in device_threads:
                    if thread.is_finished:
                        if thread.note == app_apk_log_note:
                            session_logger.log_app_apk_install_end_time_on_device(device.adb_name)
                        if thread.note == test_apk_log_note:
                            session_logger.log_test_apk_install_end_time_on_device(device.adb_name)
                    else:
                        all_threads_has_finished = False

                if not all_threads_has_finished:
                    break

            all_devices_have_apk_installed = all_threads_has_finished

    def set_instrumentation_runner_according_to(self, apk):
        Printer.system_message(self.TAG, "Scanning test .*apk file for Instrumentation Runner data.")

        resources = self.aapt_controller.list_resources(apk.test_apk_path)
        target_package = ""
        instrumentation_runner_name = ""

        inside_instrumentation_section = False
        inside_manifest_section = False
        for line in resources.splitlines():
            if "E: instrumentation" in line:
                inside_instrumentation_section = True
                continue

            if "E: manifest" in line:
                inside_manifest_section = True
                continue

            if inside_instrumentation_section and "E: " in line:
                inside_instrumentation_section = False

            if inside_manifest_section and "E: " in line:
                inside_manifest_section = False

            if inside_instrumentation_section:
                if "A: android:name" in line:
                    regex_result = re.findall("=\"(.+?)\"", line)
                    if regex_result:
                        instrumentation_runner_name = str(regex_result[0])

            if inside_manifest_section:
                if "A: package" in line:
                    regex_result = re.findall("=\"(.+?)\"", line)
                    if regex_result:
                        target_package = str(regex_result[0])

        if target_package == "":
            message = "Unable to find package of tested application in test .*apk file. Tests won't start without it."
            raise LauncherFlowInterruptedException(self.TAG, message)

        if instrumentation_runner_name == "":
            message = ("Unable to find Instrumentation Runner name of tested application in test .*apk file."
                       " Tests won't start without it.")
            raise LauncherFlowInterruptedException(self.TAG, message)

        GlobalConfig.INSTRUMENTATION_RUNNER = target_package + "/" + instrumentation_runner_name
        Printer.system_message(self.TAG, "Instrumentation Runner found: " + Color.GREEN +
                               GlobalConfig.INSTRUMENTATION_RUNNER + Color.BLUE + ".")


class TestManager:
    TAG = "TestManager:"
    DEVICE_NAME_PLACEHOLDER = "device_name_to_replace"
    RECORDING_DIR_PLACEHOLDER = "recording_dir_to_replace"

    def __init__(self, instrumentation_runner_controller, adb_controller, adb_shell_controller, logcat_controller,
                 device_store, test_store):

        self.instrumentation_runner_controller = instrumentation_runner_controller
        self.adb_controller = adb_controller
        self.adb_shell_controller = adb_shell_controller
        self.logcat_controller = logcat_controller
        self.device_store = device_store
        self.test_store = test_store

    def run_tests(self, test_set, test_list):
        devices = self.device_store.get_devices()
        test_packages = self.test_store.get_packages(test_set, test_list)

        launch_variant_string = "TESTS SPLIT INTO SHARDS" if test_set.shard else "EACH TEST ON EACH DEVICE"
        Printer.system_message(self.TAG, "According to test set settings, tests will be run with following variant: "
                               + Color.GREEN + launch_variant_string + Color.BLUE + ".")

        device_commands_dict = self._prepare_device_control_cmds(devices)
        test_cmd_templates = self._prepare_launch_test_cmds_for_run(test_packages, devices, test_set.shard)

        threads_finished = False
        logcat_threads_num = len(devices)
        recording_threads_num = len(devices) if GlobalConfig.SHOULD_RECORD_TESTS else 0
        test_threads_num = len(test_cmd_templates)

        logcat_threads = list()
        test_threads = list()
        test_log_saving_threads = list()
        logcat_saving_threads = list()
        test_recording_saving_threads = list()

        try:
            while not threads_finished:
                if len(logcat_threads) != logcat_threads_num:
                    for device in devices:
                        logcat_thread = TestLogCatMonitorThread(device,
                                                                device_commands_dict.get(device),
                                                                GlobalConfig.SHOULD_RECORD_TESTS)
                        logcat_threads.append(logcat_thread)
                        logcat_thread.start()

                if len(test_recording_saving_threads) != recording_threads_num:
                    for device in devices:
                        test_recording_saving_thread = TestRecordingSavingThread(device)
                        test_recording_saving_threads.append(test_recording_saving_thread)
                        test_recording_saving_thread.start()

                if len(test_threads) != test_threads_num and all(t.logcat_process is not None for t in logcat_threads):
                    for device in devices:
                        if not any(t.device.adb_name == device.adb_name and t.is_alive() for t in test_threads) \
                                and len(test_cmd_templates) > 0:
                            launch_cmd_template = test_cmd_templates.pop(0)
                            launch_cmd = launch_cmd_template.replace(self.DEVICE_NAME_PLACEHOLDER, device.adb_name)

                            Printer.system_message(self.TAG,
                                                   str(len(test_cmd_templates)) + " packages to run left...")

                            test_thread = TestThread(launch_cmd, device)
                            test_threads.append(test_thread)
                            test_thread.start()

                for test_thread in test_threads:
                    if len(test_thread.logs) > 0:
                        current_test_logs = copy.deepcopy(test_thread.logs)

                        for log in current_test_logs:
                            if log.test_status == "success":
                                session_logger.increment_passed_tests()

                            if log.test_status == "failure":
                                session_logger.increment_failed_tests()

                        test_log_saving_thread = TestSummarySavingThread(test_thread.device, current_test_logs)
                        test_log_saving_threads.append(test_log_saving_thread)
                        test_log_saving_thread.start()
                        test_thread.logs.clear()

                for logcat_thread in logcat_threads:
                    if len(logcat_thread.logs) > 0:
                        current_logcats = copy.deepcopy(logcat_thread.logs)
                        logcat_saving_thread = TestLogcatSavingThread(logcat_thread.device, current_logcats)
                        logcat_saving_threads.append(logcat_saving_thread)
                        logcat_saving_thread.start()
                        logcat_thread.logs.clear()

                    if len(logcat_thread.recordings) > 0:
                        device = logcat_thread.device
                        current_recordings = copy.deepcopy(logcat_thread.recordings)

                        for recording_saving_thread in test_recording_saving_threads:
                            if recording_saving_thread.device.adb_name == device.adb_name:
                                pull_cmd_list = list()
                                clear_cmd_list = list()
                                for recording_name in current_recordings:
                                    recording_dir = FileUtils.add_ending_slash(FileUtils.clean_path(
                                        GlobalConfig.DEVICE_VIDEO_STORAGE_DIR)) + recording_name
                                    pull_cmd_list.append(self._prepare_pull_recording_cmd(device, recording_dir))
                                    clear_cmd_list.append(self._prepare_remove_recording_cmd(device, recording_dir))

                                    recording_saving_thread.add_recordings(current_recordings)
                                    recording_saving_thread.add_pull_recording_cmds(pull_cmd_list)
                                    recording_saving_thread.add_clear_recordings_cmd(clear_cmd_list)

                        logcat_thread.recordings.clear()

                if len(test_threads) == test_threads_num \
                        and all(not t.is_alive() for t in test_threads) \
                        and all(t.is_finished() for t in test_log_saving_threads) \
                        and all(t.is_finished() for t in logcat_saving_threads):

                    for test_thread in test_threads:
                        test_thread.kill_processes()
                        test_thread.join()

                    for logcat_thread in logcat_threads:
                        logcat_thread.kill_processes()
                        logcat_thread.join()

                    for test_log_saving_thread in test_log_saving_threads:
                        test_log_saving_thread.join()

                    for logcat_saving_thread in logcat_saving_threads:
                        logcat_saving_thread.join()

                    test_threads.clear()
                    logcat_threads.clear()
                    test_log_saving_threads.clear()
                    logcat_saving_threads.clear()

                if len(test_recording_saving_threads) > 0 and len(logcat_threads) == 0:
                    if all(len(t.recordings) == 0 for t in test_recording_saving_threads):
                        for recording_thread in test_recording_saving_threads:
                            recording_thread.kill_processes()
                            recording_thread.join()

                        test_recording_saving_threads.clear()

                threads_finished = len(logcat_threads) == 0 and len(test_threads) == 0 and len(
                    test_log_saving_threads) == 0 and len(logcat_saving_threads) == 0 and len(
                    test_recording_saving_threads) == 0 and len(test_cmd_templates) == 0
        except Exception as e:
            message = "Error has occurred during test session: \n" + str(e)
            raise LauncherFlowInterruptedException(self.TAG, message)
        finally:
            if len(test_threads) > 0:
                for test_thread in test_threads:
                    test_thread.kill_processes()
                    test_thread.join()

            if len(logcat_threads) > 0:
                for logcat_thread in logcat_threads:
                    logcat_thread.kill_processes()
                    logcat_thread.join()

            if len(test_log_saving_threads) > 0:
                for test_log_saving_thread in test_log_saving_threads:
                    test_log_saving_thread.join()

            if len(logcat_saving_threads) > 0:
                for logcat_saving_thread in logcat_saving_threads:
                    logcat_saving_thread.join()

            if len(test_recording_saving_threads) > 0:
                for recording_thread in test_recording_saving_threads:
                    recording_thread.kill_processes()
                    recording_thread.join()

            test_threads.clear()
            logcat_threads.clear()
            test_log_saving_threads.clear()
            logcat_saving_threads.clear()
            test_recording_saving_threads.clear()

    def _prepare_pull_recording_cmd(self, device, file_dir):
        adb_cmd_assembler = self.adb_controller.adb_command_assembler
        return adb_cmd_assembler.assemble_pull_file_cmd(self.adb_shell_controller.adb_bin,
                                                        device.adb_name,
                                                        file_dir,
                                                        GlobalConfig.OUTPUT_TEST_RECORDINGS_DIR)

    def _prepare_remove_recording_cmd(self, device, file_dir):
        adb_shell_cmd_assembler = self.adb_shell_controller.adb_shell_command_assembler
        return adb_shell_cmd_assembler.assemble_remove_file_cmd(self.adb_shell_controller.adb_bin,
                                                                device.adb_name,
                                                                file_dir)

    def _prepare_device_control_cmds(self, devices):
        device_commands_dict = dict()
        for device in devices:
            monitor_logcat_cmd = self._prepare_monitor_logcat_cmd(device)
            flush_logcat_cmd = self._prepare_flush_logcat_cmd(device)
            record_screen_cmd = self._prepare_record_screen_cmd(device)
            device_commands_dict[device] = {"monitor_logcat_cmd": monitor_logcat_cmd,
                                            "flush_logcat_cmd": flush_logcat_cmd,
                                            "record_screen_cmd": record_screen_cmd}
        return device_commands_dict

    def _prepare_monitor_logcat_cmd(self, device):
        logcat_cmd_assembler = self.logcat_controller.adb_logcat_command_assembler
        return logcat_cmd_assembler.assemble_monitor_logcat_cmd(self.instrumentation_runner_controller.adb_bin,
                                                                device.adb_name)

    def _prepare_flush_logcat_cmd(self, device):
        logcat_cmd_assembler = self.logcat_controller.adb_logcat_command_assembler
        return logcat_cmd_assembler.assemble_flush_logcat_cmd(self.instrumentation_runner_controller.adb_bin,
                                                              device.adb_name)

    def _prepare_record_screen_cmd(self, device):
        adb_shell_cmd_assembler = self.adb_shell_controller.adb_shell_command_assembler
        return adb_shell_cmd_assembler.assemble_record_screen_cmd(self.adb_shell_controller.adb_bin,
                                                                  device.adb_name,
                                                                  GlobalConfig.DEVICE_VIDEO_STORAGE_DIR)

    def _prepare_launch_test_cmds_for_run(self, test_packages, devices, use_shards):

        cmd_list = list()
        for package in test_packages:
            for i in range(0, len(devices)):

                if use_shards:
                    parameters = {"package": package, "numShards": len(devices), "shardIndex": i}
                else:
                    parameters = {"package": package}

                launch_cmd = self._prepare_launch_test_cmd_for_run(parameters)
                cmd_list.append(launch_cmd)
        return cmd_list

    def _prepare_launch_test_cmd_for_run(self, parameters):
        instr_cmd_assembler = self.instrumentation_runner_controller.instrumentation_runner_command_assembler
        return instr_cmd_assembler.assemble_run_test_package_cmd(self.instrumentation_runner_controller.adb_bin,
                                                                 self.DEVICE_NAME_PLACEHOLDER,
                                                                 parameters,
                                                                 GlobalConfig.INSTRUMENTATION_RUNNER)
