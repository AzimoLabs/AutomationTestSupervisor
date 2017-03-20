from system.bin.SystemShellCommands import GeneralCommand

from android.bin.AndroidShellCommands import (
    AaptCommand,
    AdbCommand,
    AvdManagerCommand,
    EmulatorCommand,
    GradleCommand,
    InstrumentationRunnerCommand
)


class AaptCommandAssembler:
    dump_badging_schema = "{} {}"

    def assemble_dump_badging_cmd(self, aapt_bin, apk_name):
        return self.dump_badging_schema.format(aapt_bin,
                                               AaptCommand.DUMP_BADGING.format(apk_name))


class AdbCommandAssembler:
    start_server_schema = "{} {}"
    kill_server_schema = "{} {}"
    devices_schema = "{} {}"
    waif_for_device_schema = "{} {}"
    kill_device_schema = "{} {} {} {}"
    install_apk_schema = "{} {} {} {}"
    get_property_schema = "{} {} {} {}"

    def assemble_start_server_cmd(self, adb_bin):
        return self.start_server_schema.format(adb_bin,
                                               AdbCommand.START_SERVER)

    def assemble_kill_server_cmd(self, adb_bin):
        return self.kill_server_schema.format(adb_bin,
                                              AdbCommand.KILL_SERVER)

    def assemble_devices_cmd(self, adb_bin):
        return self.devices_schema.format(adb_bin,
                                          AdbCommand.DEVICES)

    def assemble_wait_for_device_cmd(self, adb_bin):
        return self.waif_for_device_schema.format(adb_bin,
                                                  AdbCommand.WAIT_FOR_DEVICE)

    def assemble_kill_device_cmd(self, adb_bin, device_adb_name):
        return self.kill_device_schema.format(adb_bin,
                                              AdbCommand.SPECIFIC_DEVICE.format(device_adb_name),
                                              AdbCommand.KILL_DEVICE)

    def assemble_install_apk_cmd(self, adb_bin, device_adb_name, apk_name):
        return self.install_apk_schema.format(adb_bin,
                                              AdbCommand.SPECIFIC_DEVICE.format(device_adb_name),
                                              AdbCommand.INSTALL_APK.format(apk_name),
                                              GeneralCommand.CHANGE_THREAD)

    def assemble_get_property_cmd(self, adb_bin, device_adb_name, device_property):
        return self.get_property_schema.format(adb_bin,
                                               AdbCommand.SPECIFIC_DEVICE.format(device_adb_name),
                                               AdbCommand.GET_PROPERTY,
                                               device_property)
