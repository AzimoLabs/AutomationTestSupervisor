from android.bin.command.AvdManagerCommand import *
from console.ShellHelper import *
from console.Printer import *
from system.command.GeneralCommand import *
from system.mapper.PathMapper import *
from settings.Settings import *

TAG = "AvdManagerController:"


class AvdManagerController:
    avdmanager_bin = None

    def __init__(self):
        self.avdmanager_bin = clean_path(add_ending_slash(Settings.SDK_DIR) + "tools/bin/avdmanager")

        if os.path.isfile(self.avdmanager_bin):
            print_message(TAG, "AvdManager binary file found at '" + self.avdmanager_bin + "'.")
        else:
            print_error(TAG, "Unable to find ADB binary at '" + self.avdmanager_bin + "'.")
            quit()

    def list_avd(self):
        return execute_shell(self.avdmanager_bin + " " + AvdManagerCommand.LIST_AVD, False, False)

    def delete_avd(self, avd_schema):
        avd_name = avd_schema.avd_name
        return execute_shell(self.avdmanager_bin + " " + AvdManagerCommand.DELETE_AVD.format(avd_name), True, True)

    def create_avd(self, avd_schema):
        part_answer_no = GeneralCommand.ANSWER_NO
        part_create_avd = AvdManagerCommand.CreateAvdCommandPart.AVD_CREATE
        part_name = AvdManagerCommand.CreateAvdCommandPart.AVD_NAME.format(avd_schema.avd_name)
        part_package = AvdManagerCommand.CreateAvdCommandPart.AVD_PACKAGE.format(avd_schema.create_avd_package)

        if avd_schema.create_avd_device == "":
            part_device = avd_schema.avd_device
        else:
            part_device = AvdManagerCommand.CreateAvdCommandPart.AVD_DEVICE.format(avd_schema.create_avd_device)

        if avd_schema.create_avd_tag == "":
            part_tag = avd_schema.create_avd_tag
        else:
            part_tag = AvdManagerCommand.CreateAvdCommandPart.AVD_TAG.format(avd_schema.create_avd_tag)

        if avd_schema.create_avd_abi == "":
            part_abi = avd_schema.create_avd_abi
        else:
            part_abi = AvdManagerCommand.CreateAvdCommandPart.AVD_ABI.format(avd_schema.create_avd_abi)

        part_avd_additional_options = AvdManagerCommand.CreateAvdCommandPart.AVD_ADDITIONAL_OPTIONS.format(
            avd_schema.create_avd_additional_options)

        create_avd_cmd = "{} {} {} {} {} {} {} {} {}".format(part_answer_no,
                                                             self.avdmanager_bin,
                                                             part_create_avd,
                                                             part_name,
                                                             part_package,
                                                             part_device,
                                                             part_tag,
                                                             part_abi,
                                                             part_avd_additional_options)
        return execute_shell(create_avd_cmd, True, True)
