from android.bin.command.AdbCommand import *
from console.ShellHelper import *
from console.Printer import *
from system.mapper.PathMapper import *
from system.command.GeneralCommand import *
from settings.Settings import *

TAG = "AdbController:"


class AdbController:
    adb_bin = None

    def __init__(self):
        self.adb_bin = clean_path(add_ending_slash(Settings.SDK_DIR) + "platform-tools/adb")

        if os.path.isfile(self.adb_bin):
            print_message(TAG, "ADB binary file found at '" + self.adb_bin + "'.")
        else:
            print_error(TAG, "Unable to find ADB binary at '" + self.adb_bin + "'.")
            quit()

    def start_server(self):
        return execute_shell(self.adb_bin + " " + AdbCommand.START_SERVER, True, True)

    def kill_server(self):
        return execute_shell(self.adb_bin + " " + AdbCommand.KILL_SERVER, True, True)

    def devices(self):
        return execute_shell(self.adb_bin + " " + AdbCommand.DEVICES, False, False)

    def wait_for_device(self):
        return execute_shell(self.adb_bin + " " + AdbCommand.WAIT_FOR_DEVICE, False, False)

    def kill_device(self, device_adb_name):
        kill_device_cmd = "{} {} {} {} {}".format(self.adb_bin,
                                                  AdbCommand.SPECIFIC_DEVICE,
                                                  device_adb_name,
                                                  AdbCommand.KILL_DEVICE,
                                                  GeneralCommand.DELEGATE_OUTPUT_TO_NULL)
        return execute_shell(kill_device_cmd, True, False)

    def install_apk(self, device_adb_name, apk_name):
        return execute_shell(self.adb_bin
                             + " " + AdbCommand.INSTALL_APK.format(device_adb_name, apk_name)
                             + " " + GeneralCommand.CHANGE_THREAD, True, False)

    def get_property(self, device_adb_name, device_property):
        get_property_cmd = "{} {} {} {} {}".format(self.adb_bin,
                                                   AdbCommand.SPECIFIC_DEVICE,
                                                   device_adb_name,
                                                   AdbCommand.GET_PROPERTY,
                                                   device_property)
        return execute_shell(get_property_cmd, False, False)
