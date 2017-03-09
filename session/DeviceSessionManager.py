import time
from threading import Thread

from android.bin.AdbController import *
from android.bin.AndroidController import *
from android.bin.EmulatorController import *
from android.device.model.AndroidVirtualDevice import *
from console.Printer import *

TAG = "DeviceSessionManager:"


class DeviceSessionManager:
    def __init__(self, device_store, adb_controller, android_controller):
        self.device_store = device_store
        self.adb_controller = adb_controller
        self.android_controller = android_controller

    def create_all_avd_and_reuse_existing(self):
        created_avd_list = re.findall("Name: (.+)", self.android_controller.list_avd())

        for device in self.device_store.devices:
            if isinstance(device, AndroidVirtualDevice):
                avd_was_created = False
                for created_avd in created_avd_list:
                    if created_avd == device.avd_schema.avd_name:
                        avd_was_created = True
                        break
                if avd_was_created:
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
        self.device_store.update_device_statuses()

        created_avd_list = re.findall("Name: (.+)", self.android_controller.list_avd())
        for device in self.device_store.devices:
            if isinstance(device, AndroidVirtualDevice):
                avd_was_created = False
                for created_avd in created_avd_list:
                    if created_avd == device.avd_schema.avd_name:
                        avd_was_created = True
                        break
                if avd_was_created:
                    print_message(TAG, "AVD with name '"
                                  + str(device.avd_schema.avd_name) + "' already exists and will be re-created.")
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
        for device in self.device_store.devices:
            if isinstance(device, AndroidVirtualDevice) and device.status == "not-launched":
                Thread(target=device.launch).start()
            self._wait_for_adb_statuses((device,))
        self._wait_for_property_statuses(self.device_store.devices)

    def launch_all_avd_at_once(self):
        for device in self.device_store.devices:
            if isinstance(device, AndroidVirtualDevice) and device.status == "not-launched":
                Thread(target=device.launch).start()
        self._wait_for_adb_statuses(self.device_store.devices)
        self._wait_for_property_statuses(self.device_store.devices)

    def _wait_for_adb_statuses(self, monitored_devices):
        print_message(TAG, "Waiting until (" + " ".join("'" + device.adb_name + "'" for device in monitored_devices) +
                      ") devices status will change to 'device'.")

        device_adb_statuses = dict()
        for device in monitored_devices:
            device_adb_statuses.update({device.adb_name: device.status})

        timeout = Settings.AVD_ADB_BOOT_TIMEOUT
        start_time = last_check_time = time.time()
        while True:
            current_time = time.time()

            if current_time - last_check_time >= Settings.AVD_LAUNCH_SCAN_INTERVAL or start_time == last_check_time:
                last_check_time = current_time

                self.device_store.update_device_statuses()
                for device in self.device_store.devices:
                    if device in monitored_devices and device.status == "device":
                        device_adb_statuses[device.adb_name] = "device"

                print_message(TAG, "Current wait status:")
                for device, status in device_adb_statuses.items():
                    print_message_highlighted(TAG, "- " + device + " ", "('" + status + "')")

                if all(device_status == "device" for device_status in device_adb_statuses.values()):
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

        start_time = last_check_time = time.time()
        while True:
            current_time = time.time()

            if current_time - last_check_time >= Settings.AVD_LAUNCH_SCAN_INTERVAL or start_time == last_check_time:
                last_check_time = current_time

                print_message(TAG, "Current wait status:")
                for device in self.device_store.devices:
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
        self.device_store.update_device_statuses()
        print_message(TAG, "Currently visible devices in session:")
        for device in self.device_store.devices:
            print_message_highlighted(TAG, "- " + device.adb_name + " ", "('" + device.status + "')")
            if isinstance(device, AndroidVirtualDevice) \
                    and self.device_store.is_avd_from_this_session(device.adb_name) \
                    and device.status != "not-launched":
                device.kill()

        self.device_store.update_device_statuses()
        print_message(TAG, "Devices in session statuses after killing:")
        for device in self.device_store.devices:
            print_message_highlighted(TAG, "- " + device.adb_name + " ", "('" + device.status + "')")
