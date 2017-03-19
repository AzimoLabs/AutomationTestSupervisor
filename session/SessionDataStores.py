import copy

from system.console import Printer
from system.file import FileUtils
from system.port import PortManager

from session.SessionDevices import (
    OutsideSessionVirtualDevice,
    OutsideSessionDevice,
    SessionVirtualDevice
)


class DeviceStore:
    TAG = "DeviceStore:"

    def __init__(self, adb_controller, android_controller, emulator_controller):
        self.adb_controller = adb_controller
        self.android_controller = android_controller
        self.emulator_controller = emulator_controller

        self.outside_session_virtual_devices = list()
        self.outside_session_devices = list()
        self.session_devices = list()

    def prepare_outside_session_devices(self):
        currently_visible_devices = self._get_visible_devices()

        for device_name, status in currently_visible_devices.items():
            if "emulator" not in device_name:
                outside_session_device = OutsideSessionDevice(device_name, status, self.adb_controller)
                Printer.system_message(self.TAG, "Android Device model representing device with name '"
                                       + device_name + "' was added to test run.")
                self.outside_session_devices.append(outside_session_device)

        if not any(isinstance(device, OutsideSessionVirtualDevice) for device in self.outside_session_devices):
            Printer.system_message(self.TAG, "No Android Devices connected to PC were found.")

    def prepare_outside_session_virtual_devices(self):
        currently_visible_devices = self._get_visible_devices()

        for device_name, status in currently_visible_devices.items():
            if "emulator" in device_name:
                outside_session_virtual_device = OutsideSessionVirtualDevice(device_name, status, self.adb_controller)
                Printer.system_message(self.TAG, "AVD model representing device with name '"
                                       + device_name + "' was added to test run.")
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
                log_file = FileUtils.create_file("avd_logs", avd_schema.avd_name, "txt")

                session_device = SessionVirtualDevice(avd_schema,
                                                      port,
                                                      log_file,
                                                      self.android_controller,
                                                      self.emulator_controller,
                                                      self.adb_controller)
                self.session_devices.append(session_device)
                Printer.system_message(self.TAG, "Android Virtual Device model was created according to schema '" +
                                       avd_schema.avd_name + "'. Instance number: " + str(i)
                                       + ". Assigned to port: " + str(port) + ".")

    def _get_visible_devices(self):
        currently_visible_devices = dict()
        adb_devices_output = self.adb_controller.devices()

        for line in adb_devices_output.splitlines():
            device_name = line.split()[0]
            device_status = line.split()[1]
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


class TestStore:
    TAG = "TestStore:"

    def __init__(self):
        self.packages_to_run = list()

    def get_packages(self, test_set, test_list):
        for package_name in test_set.set_package_names:
            for test_package in test_list[package_name].test_packages:
                if test_package not in self.packages_to_run:
                    self.packages_to_run.append(test_package)
