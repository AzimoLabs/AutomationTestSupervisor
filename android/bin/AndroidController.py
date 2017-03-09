from android.bin.command.AndroidCommand import *
from console.ShellHelper import *
from console.Printer import *
from system.command.GeneralCommand import *
from system.mapper.PathMapper import *
from settings.Settings import *

TAG = "AndroidController:"


class AndroidController:
    android_bin = None

    def __init__(self):
        self.android_bin = clean_path(add_ending_slash(Settings.SDK_DIR) + "tools/android")

        if os.path.isfile(self.android_bin):
            print_message(TAG, "Android binary file found at '" + self.android_bin + "'.")
        else:
            print_error(TAG, "Unable to find ADB binary at '" + self.android_bin + "'.")
            quit()

    def list_avd(self):
        return execute_shell(self.android_bin + " " + AndroidCommand.LIST_AVD, False, False)

    def delete_avd(self, avd_schema):
        avd_name = avd_schema.avd_name
        return execute_shell(self.android_bin + " " + AndroidCommand.DELETE_AVD.format(avd_name), True, True)

    def create_avd(self, avd_schema):
        part_answer_no = GeneralCommand.ANSWER_NO
        part_create_avd = AndroidCommand.CreateAvdCommandPart.AVD_CREATE
        part_avd_name = AndroidCommand.CreateAvdCommandPart.AVD_NAME.format(avd_schema.avd_name)
        part_avd_target = AndroidCommand.CreateAvdCommandPart.AVD_TARGET.format(avd_schema.create_avd_target)
        part_avd_abi = AndroidCommand.CreateAvdCommandPart.AVD_ABI.format(avd_schema.create_avd_abi)
        part_avd_additional_options = AndroidCommand.CreateAvdCommandPart.AVD_ADDITIONAL_OPTIONS.format(
            avd_schema.create_avd_additional_options)

        create_avd_cmd = "{} {} {} {} {} {} {}".format(part_answer_no,
                                                       self.android_bin,
                                                       part_create_avd,
                                                       part_avd_name,
                                                       part_avd_target,
                                                       part_avd_abi,
                                                       part_avd_additional_options)
        return execute_shell(create_avd_cmd, True, True)
