from android.device.model.AndroidDevice import *
from android.device.model.AndroidVirtualDevice import *
from system.manager.FileManager import *
from system.manager.OpenPortManager import *
from copy import *

TAG = "DeviceManager:"


class DeviceStore:
    is_after_ad_init = False
    is_after_avd_init = False

    def __init__(self, adb_controller, android_controller, emulator_controller):
        self.adb_controller = adb_controller
        self.android_controller = android_controller
        self.emulator_controller = emulator_controller
        self.devices = list()

    def prepare_android_device_models(self):
        if self.is_after_ad_init:
            print_message(TAG, "Android device models have been already prepared.")
            return
        else:
            self.is_after_ad_init = True

        currently_visible_devices = self._get_visible_devices()

        for device_name, status in currently_visible_devices.items():
            if "emulator" not in device_name:
                android_device = AndroidDevice(device_name, status, self.emulator_controller)
                self.devices.append(android_device)
                print_message(TAG, "Android Device model representing device with name '"
                              + device_name + "' will be used during test run.")

        if not any(isinstance(device, AndroidDevice) for device in self.devices):
            print_message(TAG, "No Android Devices connected to PC were found.")

    def prepare_android_virtual_device_models(self, avd_set, avd_schemas):
        if self.is_after_avd_init:
            print_message(TAG, "AVD models have been already prepared.")
            return
        else:
            self.is_after_avd_init = True

        avd_ports = get_open_ports(avd_set)
        for avd in avd_set.avd_list:
            instances_of_schema = avd.instances
            for i in range(instances_of_schema):
                avd_schema = deepcopy(avd_schemas[avd.avd_name])
                avd_schema.avd_name = avd_schema.avd_name + "-" + str(i)
                port = avd_ports.pop(0)
                log_file = create_txt_file("avd_logs", avd_schema.avd_name)

                android_virtual_device = AndroidVirtualDevice(avd_schema,
                                                              port,
                                                              log_file,
                                                              self.android_controller,
                                                              self.emulator_controller,
                                                              self.adb_controller)
                self.devices.append(android_virtual_device)
                print_message(TAG, "Android Virtual Device model was created according to schema '" +
                              avd_schema.avd_name + "'. Instance number: " + str(i)
                              + ". Assigned to port: " + str(port) + ".")

        self._ignore_foreign_android_virtual_devices()

    def _ignore_foreign_android_virtual_devices(self):
        currently_visible_devices = self._get_visible_devices()

        for device_name, status in currently_visible_devices.items():
            if not self.is_avd_from_this_session(device_name):
                print_error(TAG, "Android Virtual Device with name '" + device_name
                            + "' was spawned by other process and will be omitted during test run.")

    def _get_visible_devices(self):
        currently_visible_devices = dict()
        adb_devices_output = self.adb_controller.devices()

        for line in adb_devices_output.splitlines():
            device_name = line.split()[0]
            device_status = line.split()[1]
            currently_visible_devices.update({device_name: device_status})

        return currently_visible_devices

    def update_device_statuses(self):
        currently_visible_devices = self._get_visible_devices()

        for device in self.devices:
            device.status = "not-launched"

        for device_name, status in currently_visible_devices.items():
            for device in self.devices:
                if device.adb_name == device_name:
                    device.status = status

    def is_avd_from_this_session(self, avd_name):
        avd_found = False
        for device in self.devices:
            if device.adb_name == avd_name and "emulator" in device.adb_name:
                avd_found = True
                break
        return avd_found

    def is_device_from_this_session(self, device_name):
        device_found = False
        for device in self.devices:
            if device.adb_name == device_name:
                device_found = True
                break
        return device_found
