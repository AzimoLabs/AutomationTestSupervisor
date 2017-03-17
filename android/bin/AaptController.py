from console.ShellHelper import *
from console.Printer import *
from system.mapper.PathMapper import *
from settings.Settings import *
from android.bin.command.AaptCommand import *
import re

TAG = "AaptController:"


class AaptController:
    aapt_bin = None

    def __init__(self):
        build_tools = os.listdir(clean_path(add_ending_slash(Settings.SDK_DIR) + "build-tools"))
        build_tools = [build_tool for build_tool in build_tools if build_tool[0].isdigit()]

        build_tools_folder_with_highest_ver = None
        print_message(TAG, "Available Android SDK Build-Tools versions: " + str(build_tools))
        for build_tools_folder in build_tools:
            if build_tools_folder_with_highest_ver is None:
                build_tools_folder_with_highest_ver = build_tools_folder
                continue

            ver = int(re.sub("[^0-9]", "", build_tools_folder))
            highest_ver = int(re.sub("[^0-9]", "", build_tools_folder_with_highest_ver))

            if ver > highest_ver:
                build_tools_folder_with_highest_ver = build_tools_folder

        if build_tools_folder_with_highest_ver is None:
            print_error(TAG, "Android SDK Build-Tools not found. Launcher will quit.")
            quit()
        else:
            print_message_highlighted(TAG, "Android SDK Build-Tools with latest version were selected: ",
                                      str(build_tools_folder_with_highest_ver))

        self.aapt_bin = clean_path(add_ending_slash(Settings.SDK_DIR) + "build-tools/"
                                   + str(build_tools_folder_with_highest_ver) + "/aapt")

        if os.path.isfile(self.aapt_bin):
            print_message(TAG, "Aapt binary file found at '" + self.aapt_bin + "'.")
        else:
            print_error(TAG, "Unable to find Aapt binary at '" + self.aapt_bin + "'.")
            quit()

    def dump_badging(self, apk_name):
        return execute_shell(self.aapt_bin + " " + AaptCommand.DUMP_BADGING.format(apk_name), False, False)
