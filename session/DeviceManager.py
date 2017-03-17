from android.bin.AdbController import *
from android.bin.AvdManagerController import *
from android.bin.EmulatorController import *
from android.device.model.OutsideSessionVirtualDevice import *
from android.device.model.SessionVirtualDevice import *
from session.thread.ApkInstallThread import *
from console.Printer import *
from console.Color import *

TAG = "DeviceManager:"


class DeviceManager:
    def __init__(self, device_store, adb_controller, android_controller):
        self.device_store = device_store
        self.adb_controller = adb_controller
        self.android_controller = android_controller

    def add_models_based_on_avd_schema(self, avd_set, avd_schemas):
        self.device_store.prepare_session_devices(avd_set, avd_schemas)

    def add_models_representing_outside_session_devices(self):
        self.device_store.prepare_outside_session_devices()

    def create_all_avd_and_reuse_existing(self):
        created_avd_list = re.findall("Name: (.+)", self.android_controller.list_avd())

        for device in self.device_store.get_devices():
            if isinstance(device, SessionVirtualDevice):
                if device.avd_schema.avd_name in created_avd_list:
                    print_message(TAG, "AVD with name '"
                                  + str(device.avd_schema.avd_name) + "' currently exists and will be reused.")
                else:
                    device.create()

                if device.avd_schema.create_avd_hardware_config_filepath != "":
                    print_message(TAG, "'config.ini' file was specified in AVD schema of device '" + device.adb_name +
                                  " in location '" + device.avd_schema.create_avd_hardware_config_filepath +
                                  "'. Applying...")
                    device.apply_config_ini()

    def create_all_avd_and_recreate_existing(self):
        created_avd_list = re.findall("Name: (.+)", self.android_controller.list_avd())

        for device in self.device_store.get_devices():
            if isinstance(device, SessionVirtualDevice):
                if device.avd_schema.avd_name in created_avd_list:
                    print_message(TAG, "AVD with name '"
                                  + device.avd_schema.avd_name + "' already exists and will be re-created.")
                    device.delete()
                    device.create()
                else:
                    device.create()

            if device.avd_schema.create_avd_hardware_config_filepath != "":
                print_message(TAG, "'config.ini' file was specified in AVD schema of device '" + device.adb_name +
                              " in location '" + device.avd_schema.create_avd_hardware_config_filepath +
                              "'. Applying...")
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
        print_message(TAG, "Waiting until (" + " ".join("'" + device.adb_name + "'" for device in monitored_devices) +
                      ") devices status will change to '" + status + "'.")

        timeout = Settings.AVD_ADB_BOOT_TIMEOUT
        start_time = last_check_time = time.time() * 1000
        while True:
            current_time = time.time() * 1000

            if current_time - last_check_time >= Settings.AVD_LAUNCH_SCAN_INTERVAL or start_time == last_check_time:
                last_check_time = current_time

                self.device_store.update_model_statuses()
                print_message(TAG, "Current wait status:")
                for device in monitored_devices:
                    print_message_highlighted(TAG, "- " + device.adb_name + " ", "('" + device.status + "')")

                if all(device.status == status for device in monitored_devices):
                    break

            if current_time - start_time >= timeout:
                print_error(TAG, "Devices took longer than " + str(timeout)
                            + " seconds to launch (ADB launch). Timeout quit.")
                quit()

        print_message(TAG, "ADB launch finished with success!")

    def _wait_for_property_statuses(self, monitored_devices):
        print_message(TAG, "Waiting for 'dev.bootcomplete', 'sys.boot_completed', 'init.svc.bootanim', properties of"
                           " devices (" + " ".join("'" + device.adb_name + "'" for device in monitored_devices) + ").")

        device_statuses = dict()
        for device in monitored_devices:
            device_statuses.update({device.adb_name: None})

        start_time = last_check_time = time.time() * 1000
        while True:
            current_time = time.time() * 1000

            if current_time - last_check_time >= Settings.AVD_LAUNCH_SCAN_INTERVAL or start_time == last_check_time:
                last_check_time = current_time

                print_message(TAG, "Current wait status:")
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
                    print_message_highlighted(TAG, device_name + " properties: "
                                              + "('dev.bootcomplete'" + " : "
                                              + str(status_dict["dev.bootcomplete"]
                                                    if status_dict["dev.bootcomplete"] != "" else "0") + ", "
                                              + "'sys.boot_completed'" + " : "
                                              + str(status_dict["sys.boot_completed"]
                                                    if status_dict["sys.boot_completed"] != "" else "0") + ", "
                                              + "'init.svc.bootanim'" + " : " + str(status_dict["init.svc.bootanim"])
                                              + ") - ", "launched" if status_dict["boot_finished"] else "not-launched")

                if all(status_dict["boot_finished"] for status_dict in device_statuses.values()):
                    break

            if current_time - start_time >= Settings.AVD_SYSTEM_BOOT_TIMEOUT:
                print_error(TAG, "Devices took longer than " + str(Settings.AVD_SYSTEM_BOOT_TIMEOUT)
                            + " seconds to launch (Property launch). Timeout quit.")
                quit()

        print_message(TAG, "Property launch finished with success!")

    def kill_all_avd(self):
        self.device_store.update_model_statuses()
        print_message(TAG, "Currently visible AVD:")

        avd_list = list()
        for device in self.device_store.get_devices():
            if isinstance(device, OutsideSessionVirtualDevice) or isinstance(device, SessionVirtualDevice):
                avd_list.append(device)
                print_message_highlighted(TAG, "- " + device.adb_name + " ", "('" + device.status + "')")
                if device.status != "not-launched":
                    device.kill()

        self._wait_for_adb_statuses_change_to("not-launched", avd_list)
        self.device_store.update_model_statuses()
        print_message(TAG, "AVD statuses in session after killing:")
        for device in self.device_store.get_devices():
            if isinstance(device, OutsideSessionVirtualDevice) or isinstance(device, SessionVirtualDevice):
                print_message_highlighted(TAG, "- " + device.adb_name + " ", "('" + device.status + "')")

    def install_apk_on_devices(self, apk):
        if not self.device_store.get_devices():
            print_error(TAG, "No devices were found in test session. Launcher will quit.")
            quit()

        self._install_apk(apk.apk_name, apk.apk_path)
        self._install_apk(apk.test_apk_name, apk.test_apk_path)

    def _install_apk(self, apk_name, apk_path):
        print_message_highlighted(TAG, "Attempting to install " + Color.GREEN + "'" + apk_name + "'" + Color.BLUE
                                  + " on devices: ", "("
                                  + " ".join("'" + device.adb_name + "'" for device in self.device_store.get_devices())
                                  + ").")

        apk_install_threads = list()
        for device in self.device_store.get_devices():
            if device.status == "device":
                apk_install_thread = ApkInstallThread(device, apk_path)
                apk_install_thread.start()
                apk_install_threads.append(apk_install_thread)
            else:
                print_error(TAG, ".*apk won't be installed on device with name '" + device.adb_name
                            + "' because it's ADB status is set to '" + device.status + "' instead of 'device'.")

        while any(not thread.is_finished for thread in apk_install_threads):
            time.sleep(1)

    def is_any_avd_visible(self):
        self.device_store.update_model_statuses()
        return any("emulator" in device.adb_name for device in self.device_store.get_devices())
