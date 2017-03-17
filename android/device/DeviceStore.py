from android.device.model.OutsideSessionVirtualDevice import *
from android.device.model.OutsideSessionDevice import *
from android.device.model.SessionVirtualDevice import *
from system.manager.FileManager import *
from system.manager.OpenPortManager import *
from copy import *

TAG = "DeviceManager:"


class DeviceStore:
    def __init__(self, adb_controller, android_controller, emulator_controller):
        self.adb_controller = adb_controller
        self.android_controller = android_controller
        self.emulator_controller = emulator_controller
        self.outside_session_devices = list()
        self.session_devices = list()

    def prepare_outside_session_devices(self):
        currently_visible_devices = self._get_visible_devices()

        for device_name, status in currently_visible_devices.items():
            if "emulator" in device_name:
                outside_session_device = OutsideSessionVirtualDevice(device_name, status, self.adb_controller)
                print_message(TAG, "AVD model representing device with name '"
                              + device_name + "' was added to test run.")
            else:
                outside_session_device = OutsideSessionDevice(device_name, status, self.adb_controller)
                print_message(TAG, "Android Device model representing device with name '"
                              + device_name + "' was added to test run.")
            self.outside_session_devices.append(outside_session_device)

        if not any(isinstance(device, OutsideSessionDevice) or isinstance(device, OutsideSessionVirtualDevice) for
                   device in self.outside_session_devices):
            print_message(TAG, "No Android Devices connected to PC or launched AVD were found.")

    def prepare_session_devices(self, avd_set, avd_schemas):
        avd_ports = get_open_ports(avd_set)
        for avd in avd_set.avd_list:
            instances_of_schema = avd.instances
            for i in range(instances_of_schema):
                avd_schema = deepcopy(avd_schemas[avd.avd_name])
                avd_schema.avd_name = avd_schema.avd_name + "-" + str(i)
                port = avd_ports.pop(0)
                log_file = create_txt_file("avd_logs", avd_schema.avd_name)

                session_device = SessionVirtualDevice(avd_schema,
                                                      port,
                                                      log_file,
                                                      self.android_controller,
                                                      self.emulator_controller,
                                                      self.adb_controller)
                self.session_devices.append(session_device)
                print_message(TAG, "Android Virtual Device model was created according to schema '" +
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
        return self.session_devices + self.outside_session_devices

    def update_model_statuses(self):
        currently_visible_devices = self._get_visible_devices()

        for session_device in self.session_devices:
            session_device.status = "not-launched"

        for outside_session_device in self.outside_session_devices:
            outside_session_device.status = "not-launched"

        for device_name, status in currently_visible_devices.items():
            for session_device in self.session_devices:
                if session_device == device_name:
                    session_device.status = status

            for outside_session_device in self.outside_session_devices:
                if outside_session_device == device_name:
                    outside_session_device.status = status

    def clear_models_by_adb_devices(self):
        currently_visible_devices = self._get_visible_devices()

        for session_device in self.session_devices:
            if session_device.adb_name not in currently_visible_devices:
                self.session_devices.remove(session_device)

        for outside_session_device in self.outside_session_devices:
            if outside_session_device.adb_name not in currently_visible_devices:
                self.outside_session_devices.remove(outside_session_device)
