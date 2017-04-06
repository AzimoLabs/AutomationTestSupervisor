import re
import time

from error.Exceptions import LauncherFlowInterruptedException

from settings import GlobalConfig

from session.SessionModels import (
    OutsideSessionVirtualDevice,
    SessionVirtualDevice
)
from session.SessionThreads import (
    TestThread,
    ApkInstallThread
)

from system.console import (
    Printer,
    Color
)


class ApkManager:
    TAG = "ApkManager:"

    def __init__(self, device_store, apk_store, gradle_controller, aapt_controller):
        self.device_store = device_store
        self.apk_store = apk_store
        self.gradle_controller = gradle_controller
        self.aapt_controller = aapt_controller

    def get_apk(self, test_set):
        apk_candidate = self.apk_store.provide_apk(test_set)
        if apk_candidate is not None:
            Printer.message_highlighted(self.TAG, "Picked .*apk with highest version code:\n", str(apk_candidate))
        return apk_candidate

    def build_apk(self, test_set):
        Printer.system_message(self.TAG, "Building application and test .*apk from scratch.")
        self.gradle_controller.build_application_apk(test_set)
        self.gradle_controller.build_test_apk(test_set)

        apk_candidate = self.apk_store.provide_apk(test_set)
        if apk_candidate is None:
            message = "No .apk* candidates for test session were found. Check your config. Launcher will quit."
            raise LauncherFlowInterruptedException(self.TAG, message)
        else:
            Printer.message_highlighted(self.TAG, "Picked .*apk with highest version code:\n", str(apk_candidate))
        return apk_candidate

    def install_apk_on_devices(self, apk):
        if not self.device_store.get_devices():
            message = "No devices were found in test session. Launcher will quit."
            message = message.format(str(GlobalConfig.AVD_SYSTEM_BOOT_TIMEOUT))
            raise LauncherFlowInterruptedException(self.TAG, message)

        # TODO it should be one install_apk process instead of two
        # TODO (now 2nd can start only when all threads from 1st are done)
        self._install_apk(apk.apk_name, apk.apk_path)
        self._install_apk(apk.test_apk_name, apk.test_apk_path)

    def _install_apk(self, apk_name, apk_path):
        aapt_command_assembler = self.aapt_controller.aapt_command_assembler
        dump_badging_cmd = aapt_command_assembler.assemble_dump_badging_cmd(self.aapt_controller.aapt_bin, apk_path)

        Printer.message_highlighted(self.TAG, "Attempting to install " + Color.GREEN + "'" + apk_name + "'" + Color.BLUE
                                    + " on devices: ", "("
                                    + " ".join("'" + device.adb_name + "'"
                                               for device in self.device_store.get_devices())
                                    + ").")

        apk_install_threads = list()
        for device in self.device_store.get_devices():
            if device.status == "device":
                apk_install_thread = ApkInstallThread(dump_badging_cmd, device, apk_name, apk_path)
                apk_install_thread.start()
                apk_install_threads.append(apk_install_thread)
            else:
                Printer.error(self.TAG, ".*apk won't be installed on device with name '" + device.adb_name
                              + "' because it's ADB status is set to '" + device.status + "' instead of 'device'.")

        while any(not thread.is_finished for thread in apk_install_threads):
            time.sleep(1)

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
        Printer.message_highlighted(self.TAG, "Instrumentation Runner found: ", GlobalConfig.INSTRUMENTATION_RUNNER)


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
            if device.android_id in GlobalConfig.IGNORED_DEVICE_LIST:
                Printer.system_message(self.TAG, "Android-ID "
                                       + Color.GREEN + "'" + device.android_id + "'" + Color.BLUE +
                                       " of device " + Color.GREEN + "'" + device.adb_name + "'" + Color.BLUE +
                                       " was found in ignore list.")
                self.device_store.remove_device_from_session(device)

    def create_all_avd_and_reuse_existing(self):
        created_avd_list = re.findall("Name: (.+)", self.avdmanager_controller.list_avd())

        for device in self.device_store.get_devices():
            if isinstance(device, SessionVirtualDevice):

                start_time = int(round(time.time() * 1000))
                if device.avd_schema.avd_name in created_avd_list:
                    Printer.system_message(self.TAG, "AVD with name '"
                                           + str(device.avd_schema.avd_name) + "' currently exists and will be reused.")
                else:
                    device.create()

                if device.avd_schema.create_avd_hardware_config_filepath != "":
                    Printer.system_message(self.TAG,
                                           "'config.ini' file was specified in AVD schema of device '"
                                           + device.adb_name + " in location '"
                                           + device.avd_schema.create_avd_hardware_config_filepath + "'. Applying...")
                    device.apply_config_ini()
                end_time = int(round(time.time() * 1000))

                creation_time = (end_time - start_time) / 1000
                reasonable_time = 25
                if creation_time > reasonable_time and "--force" not in device.avd_schema.create_avd_additional_options:
                    Printer.message_highlighted(self.TAG, "AVD creation took: ", str(creation_time) + " sec" + Color.RED
                                                + " (Attention! Creation process could ran faster. Try adding '--force'"
                                                  " to your AVD schema in 'create_avd_additional_options' field.)")
                else:
                    Printer.message_highlighted(self.TAG, "AVD creation took: ", str(creation_time) + Color.BLUE +
                                                " seconds.")

    def create_all_avd_and_recreate_existing(self):
        created_avd_list = re.findall("Name: (.+)", self.avdmanager_controller.list_avd())

        for device in self.device_store.get_devices():
            if isinstance(device, SessionVirtualDevice):

                start_time = int(round(time.time() * 1000))
                if device.avd_schema.avd_name in created_avd_list:
                    Printer.system_message(self.TAG, "AVD with name '"
                                           + device.avd_schema.avd_name + "' already exists and will be re-created.")
                    device.delete()
                    device.create()
                else:
                    device.create()

                if device.avd_schema.create_avd_hardware_config_filepath != "":
                    Printer.system_message(self.TAG,
                                           "'config.ini' file was specified in AVD schema of device '"
                                           + device.adb_name + " in location '"
                                           + device.avd_schema.create_avd_hardware_config_filepath + "'. Applying...")
                    device.apply_config_ini()
                end_time = int(round(time.time() * 1000))

                creation_time = (end_time - start_time) / 1000
                reasonable_time = 25
                if creation_time > reasonable_time and "--force" not in device.avd_schema.create_avd_additional_options:
                    Printer.message_highlighted(self.TAG, "AVD creation took: ", str(creation_time) + " sec" + Color.RED
                                                + " (Attention! Creation process could ran faster. Try adding '--force'"
                                                " to your AVD schema in 'create_avd_additional_options' field.)")
                else:
                    Printer.message_highlighted(self.TAG, "AVD creation took: ", str(creation_time) + " sec")

    def launch_all_avd_sequentially(self):
        for device in self.device_store.get_devices():
            if isinstance(device, SessionVirtualDevice) and device.status == "not-launched":
                device.launch()
            self._wait_for_adb_statuses_change_to("device", (device,))
        self._wait_for_property_statuses(self.device_store.get_devices())

    def launch_all_avd_at_once(self):
        for device in self.device_store.get_devices():
            if isinstance(device, SessionVirtualDevice) and device.status == "not-launched":
                device.launch()
        self._wait_for_adb_statuses_change_to("device", self.device_store.get_devices())
        self._wait_for_property_statuses(self.device_store.get_devices())

    def _wait_for_adb_statuses_change_to(self, status, monitored_devices):
        Printer.system_message(self.TAG, "Waiting until ("
                               + " ".join("'" + device.adb_name + "'" for device in monitored_devices) +
                               ") devices status will change to '" + status + "'.")

        timeout = GlobalConfig.AVD_ADB_BOOT_TIMEOUT
        start_time = last_check_time = time.time() * 1000
        while True:
            current_time = time.time() * 1000

            if current_time - last_check_time >= GlobalConfig.ADB_SCAN_INTERVAL or start_time == last_check_time:
                last_check_time = current_time

                self.device_store.update_model_statuses()
                Printer.system_message(self.TAG, "Current wait status:")
                for device in monitored_devices:
                    Printer.message_highlighted(self.TAG, "- " + device.adb_name + " ", "('" + device.status + "')")

                if all(device.status == status for device in monitored_devices):
                    break

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

        start_time = last_check_time = time.time() * 1000
        while True:
            current_time = time.time() * 1000

            if current_time - last_check_time >= GlobalConfig.ADB_SCAN_INTERVAL or start_time == last_check_time:
                last_check_time = current_time

                Printer.system_message(self.TAG, "Current wait status:")
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

                for device_name, status_dict in device_statuses.items():
                    Printer.message_highlighted(self.TAG, device_name + " properties: "
                                                + "('dev.bootcomplete'" + " : "
                                                + str(status_dict["dev.bootcomplete"]
                                                      if status_dict["dev.bootcomplete"] != "" else "0") + ", "
                                                + "'sys.boot_completed'" + " : "
                                                + str(status_dict["sys.boot_completed"]
                                                      if status_dict["sys.boot_completed"] != "" else "0") + ", "
                                                + "'init.svc.bootanim'" + " : " + str(status_dict["init.svc.bootanim"])
                                                + ") - ",
                                                "launched" if status_dict["boot_finished"] else "not-launched")

                if all(status_dict["boot_finished"] for status_dict in device_statuses.values()):
                    break

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
                Printer.message_highlighted(self.TAG, "- " + device.adb_name + " ", "('" + device.status + "')")
                if device.status != "not-launched":
                    device.kill()
                    time.sleep(2)

        self._wait_for_adb_statuses_change_to("not-launched", avd_list)

    def is_any_avd_visible(self):
        self.device_store.update_model_statuses()
        return any("emulator" in device.adb_name for device in self.device_store.get_devices())


class TestManager:
    TAG = "TestManager:"

    def __init__(self, instrumentation_runner_controller, device_store, test_store):
        self.instrumentation_runner_controller = instrumentation_runner_controller
        self.device_store = device_store
        self.test_store = test_store

    def run_tests(self, test_set, test_list):
        self.test_store.get_packages(test_set, test_list)
        cmd_assembler = self.instrumentation_runner_controller.instrumentation_runner_command_assembler

        for package in self.test_store.packages_to_run:
            test_threads = list()
            for device in self.device_store.get_devices():

                params = {"package": package}
                cmd = cmd_assembler.assemble_run_test_package_cmd(self.instrumentation_runner_controller.adb_bin,
                                                                  device.adb_name,
                                                                  params,
                                                                  GlobalConfig.INSTRUMENTATION_RUNNER)

                if device.status == "device":
                    test_thread = TestThread(cmd, device)
                    test_thread.start()
                    test_threads.append(test_thread)
                else:
                    message = ("Something went wrong. At this point all devices should be ready to run. Make sure "
                               "nothing modifies status of currently connected devices.")
                    raise LauncherFlowInterruptedException(self.TAG, message)

            while any(not thread.is_finished for thread in test_threads):
                time.sleep(1)

    def run_with_boosted_shards(self, test_set, test_list):
        self.test_store.get_packages(test_set, test_list)
        cmd_assembler = self.instrumentation_runner_controller.instrumentation_runner_command_assembler

        device_name_mark = "device_name_to_replace"
        num_devices = len(self.device_store.get_devices())

        test_cmd_to_run = list()
        for package in self.test_store.packages_to_run:
            for i in range(0, num_devices):
                params = {"package": package, "numShards": num_devices, "shardIndex": i}
                cmd = cmd_assembler.assemble_run_test_package_cmd(self.instrumentation_runner_controller.adb_bin,
                                                                  device_name_mark,
                                                                  params,
                                                                  GlobalConfig.INSTRUMENTATION_RUNNER)
                test_cmd_to_run.append(cmd)

        num_test_processes_to_run = len(test_cmd_to_run)
        num_test_processes_finished = 0

        test_start = time.time()
        test_threads = list()
        while num_test_processes_to_run != num_test_processes_finished:
            for device in self.device_store.get_devices():
                is_device_thread_created = False

                threads_to_clean = list()
                for thread in test_threads:
                    if thread.device.adb_name == device.adb_name:
                        is_device_thread_created = True

                    if thread.device.adb_name == device.adb_name and thread.is_finished:
                        num_test_processes_finished += 1
                        threads_to_clean.append(thread)

                for thread in threads_to_clean:
                    test_threads.remove(thread)
                    is_device_thread_created = False

                if not is_device_thread_created and len(test_cmd_to_run) > 0:
                    if device.status == "device":
                        cmd = test_cmd_to_run.pop(0)
                        cmd = cmd.replace(device_name_mark, device.adb_name)

                        Printer.system_message(self.TAG, str(len(test_cmd_to_run)) + " packages to run left...")

                        test_thread = TestThread(cmd, device)
                        test_thread.start()
                        test_threads.append(test_thread)
                    else:
                        message = ("Something went wrong. At this point all devices should be ready to run. Make sure "
                                   "nothing modifies status of currently connected devices.")
                        raise LauncherFlowInterruptedException(self.TAG, message)

        test_end = time.time()
        Printer.message_highlighted(self.TAG,
                                    "Test process took: ", "{:.2f}".format(test_end - test_start)
                                    + Color.BLUE + " seconds.")
