from error.Exceptions import LauncherFlowInterruptedException

from settings import GlobalConfig
from session.SessionDevices import (
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

import re
import time


# TODO REMOVE STEPS FROM APK MANAGER
class ApkManager:
    TAG = "ApkManager:"

    def __init__(self, gradle_controller, apk_provider):
        self.gradle_controller = gradle_controller
        self.apk_provider = apk_provider

    def get_apk_and_build_if_not_found(self, test_set):
        apk_candidate = self.apk_provider.provide_apk(test_set)
        if apk_candidate is None:
            Printer.error(self.TAG, "No .apk* candidates for test session were found.")

            Printer.step(self.TAG, "Building application and test .*apk from scratch.")
            self.gradle_controller.build_application_apk(test_set)
            self.gradle_controller.build_test_apk(test_set)

            apk_candidate = self.apk_provider.provide_apk(test_set)
            if apk_candidate is None:
                message = "No .apk* candidates for test session were found. Check your config. Launcher will quit."
                raise LauncherFlowInterruptedException(self.TAG, message)
        return apk_candidate

    def build_apk(self, test_set):
        Printer.step(self.TAG, "Building application and test .*apk from scratch.")
        self.gradle_controller.build_application_apk(test_set)
        self.gradle_controller.build_test_apk(test_set)

        apk_candidate = self.apk_provider.provide_apk(test_set)
        if apk_candidate is None:
            message = "No .apk* candidates for test session were found. Check your config. Launcher will quit."
            raise LauncherFlowInterruptedException(self.TAG, message)
        return apk_candidate


class DeviceManager:
    TAG = "DeviceManager:"

    def __init__(self, device_store, adb_controller, android_controller):
        self.device_store = device_store
        self.adb_controller = adb_controller
        self.android_controller = android_controller

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

    def create_all_avd_and_reuse_existing(self):
        created_avd_list = re.findall("Name: (.+)", self.android_controller.list_avd())

        for device in self.device_store.get_devices():
            if isinstance(device, SessionVirtualDevice):
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

    def create_all_avd_and_recreate_existing(self):
        created_avd_list = re.findall("Name: (.+)", self.android_controller.list_avd())

        for device in self.device_store.get_devices():
            if isinstance(device, SessionVirtualDevice):
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
                        dev_boot = (self.adb_controller.get_property(device.adb_name, "dev.bootcomplete")).strip()
                        sys_boot = (self.adb_controller.get_property(device.adb_name, "sys.boot_completed")).strip()
                        boot_anim = (self.adb_controller.get_property(device.adb_name, "init.svc.bootanim")).strip()
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

    def install_apk_on_devices(self, apk):
        if not self.device_store.get_devices():
            message = "No devices were found in test session. Launcher will quit."
            message = message.format(str(GlobalConfig.AVD_SYSTEM_BOOT_TIMEOUT))
            raise LauncherFlowInterruptedException(self.TAG, message)

        self._install_apk(apk.apk_name, apk.apk_path)
        self._install_apk(apk.test_apk_name, apk.test_apk_path)

    def _install_apk(self, apk_name, apk_path):
        Printer.message_highlighted(self.TAG, "Attempting to install " + Color.GREEN + "'" + apk_name + "'" + Color.BLUE
                                    + " on devices: ", "("
                                    + " ".join("'" + device.adb_name + "'"
                                               for device in self.device_store.get_devices())
                                    + ").")

        apk_install_threads = list()
        for device in self.device_store.get_devices():
            if device.status == "device":
                apk_install_thread = ApkInstallThread(device, apk_path)
                apk_install_thread.start()
                apk_install_threads.append(apk_install_thread)
            else:
                Printer.error(self.TAG, ".*apk won't be installed on device with name '" + device.adb_name
                              + "' because it's ADB status is set to '" + device.status + "' instead of 'device'.")

        while any(not thread.is_finished for thread in apk_install_threads):
            time.sleep(1)

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

        for package in self.test_store.packages_to_run:
            test_threads = list()
            for device in self.device_store.get_devices():
                cmd = self.instrumentation_runner_controller.assemble_run_test_package_cmd(device.adb_name, package)
                if device.status == "device":
                    test_thread = TestThread(cmd, device.adb_name)
                    test_thread.start()
                    test_threads.append(test_thread)
                else:
                    Printer.error(self.TAG, "ALAOSDOASODAKSODASKDA")

            while any(not thread.is_finished for thread in test_threads):
                time.sleep(1)

    # TEMPORARY UGLY CODE
    def run_with_shards(self, test_set, test_list):
        self.test_store.get_packages(test_set, test_list)

        test_start = time.time()

        device_down_times = dict()
        device_run_times = dict()
        for device in self.device_store.get_devices():
            device_down_times.update({device.adb_name: 0})
            device_run_times.update({device.adb_name: 0})

        index = -1
        for package in self.test_store.packages_to_run:
            test_threads = list()
            for device in self.device_store.get_devices():
                index += 1
                devices_num = len(self.device_store.get_devices())
                cmd = "{} {} {} {} {} {} {}".format("/Users/F1sherKK/Library/Android/sdk/platform-tools/adb",
                                                    "-s " + device.adb_name,
                                                    "shell am instrument -w",
                                                    "-e numShards " + str(devices_num),
                                                    "-e shardIndex " + str(index),
                                                    "-e package " + package,
                                                    "com.azimo.sendmoney.debug1.test/com.azimo.sendmoney.instrumentation.config.AzimoTestRunner")
                if device.status == "device":
                    test_thread = TestThread(cmd, device.adb_name)
                    test_thread.start()
                    test_threads.append(test_thread)
                else:
                    Printer.error(self.TAG, "ALAOSDOASODAKSODASKDA")

            while any(not thread.is_finished for thread in test_threads):
                time.sleep(1)
                for thread in test_threads:
                    if thread.is_finished:
                        device_down_times[thread.device_name] += 1
                    else:
                        device_run_times[thread.device_name] += 1

        for device in self.device_store.get_devices():
            Printer.message_highlighted(self.TAG, "Device '" + device.adb_name + "' ran tests for: ",
                                        str(device_run_times[device.adb_name]) + " seconds.")

        Printer.system_message(self.TAG, "")

        for device in self.device_store.get_devices():
            Printer.message_highlighted(self.TAG, "Device '" + device.adb_name + "' waited for: ",
                                        str(device_down_times[device.adb_name]) + " seconds.")

        Printer.system_message(self.TAG, "")

        test_end = time.time()
        Printer.message_highlighted(self.TAG, "Test process took:", str((test_end - test_start)) + " seconds.")

