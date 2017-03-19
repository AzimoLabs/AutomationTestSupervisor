import re
import os
import glob

from .ApkModels import ApkCandidate
from settings import GlobalConfig
from system.console import (
    Printer,
    Color
)


def get_list_with_application_apk(apk_name_part_cleaned):
    apk_filenames = os.listdir(GlobalConfig.APK_DIR)

    application_apk_list = list()
    for apk_filename in apk_filenames:
        if apk_name_part_cleaned in apk_filename and "androidTest" not in apk_filename:
            application_apk_list.append(apk_filename)
    return application_apk_list


def get_list_with_application_apk_filepath(apk_name_part_cleaned):
    apk_absolute_paths = glob.glob(GlobalConfig.APK_DIR + "*")

    application_apk_filepath_list = list()
    for apk_path in apk_absolute_paths:
        if apk_name_part_cleaned in apk_path and "androidTest" not in apk_path:
            application_apk_filepath_list.append(apk_path)
    return application_apk_filepath_list


def get_list_with_test_apk(apk_name_part_cleaned):
    apk_filenames = os.listdir(GlobalConfig.APK_DIR)

    test_apk_list = list()
    for apk_filename in apk_filenames:
        if apk_name_part_cleaned in apk_filename and "androidTest" in apk_filename:
            test_apk_list.append(apk_filename)
    return test_apk_list


def get_list_with_test_apk_filepath(apk_name_part_cleaned):
    apk_absolute_paths = glob.glob(GlobalConfig.APK_DIR + "*")

    application_apk_filepath_list = list()
    for apk_path in apk_absolute_paths:
        if apk_name_part_cleaned in apk_path and "androidTest" in apk_path:
            application_apk_filepath_list.append(apk_path)
    return application_apk_filepath_list


class ApkProvider:
    TAG = "ApkProvider:"

    def __init__(self, aapt_controller):
        self.aapt_controller = aapt_controller
        self.apk_candidates = list()

        if os.path.isdir(GlobalConfig.APK_DIR):
            Printer.system_message(self.TAG, "Directory '" + GlobalConfig.APK_DIR + "' was found.")
        else:
            Printer.error(self.TAG, "Directory '" + GlobalConfig.APK_DIR + "' does not exist. Launcher will quit.")
            quit()

    def provide_apk(self, test_set):
        self._find_candidates(test_set)
        self._display_candidates()
        return self._get_usable_apk_candidate_for_latest_version()

    def _find_candidates(self, test_set):
        apk_name_part_cleaned = test_set.apk_name_part.replace(".apk", "")
        Printer.system_message(self.TAG,
                               "Checking '" + GlobalConfig.APK_DIR + "' directory for .*apk list with names " +
                               "containing '" + apk_name_part_cleaned + "':")

        application_apk_list = get_list_with_application_apk(apk_name_part_cleaned)
        application_apk_filepath_list = get_list_with_application_apk_filepath(apk_name_part_cleaned)
        test_apk_list = get_list_with_test_apk(apk_name_part_cleaned)
        test_apk_filepath_list = get_list_with_test_apk_filepath(apk_name_part_cleaned)

        for apk in application_apk_list:
            apk_filename = apk
            apk_filename_without_extension = apk_filename.replace(".apk", "")

            apk_filepath = ""
            for path in application_apk_filepath_list:
                if apk_filename_without_extension and "-androidTest" not in path:
                    apk_filepath = path

            version_code = -1
            if apk_filepath is not None:
                dump = self.aapt_controller.dump_badging(apk_filepath)
                version_code = re.findall("versionCode='(.+?)'", dump)
                version_code = int(version_code[0])

            apk_test_filename = ""
            for apk_name in test_apk_list:
                if apk_filename_without_extension in apk_name and "-androidTest" in apk_name:
                    apk_test_filename = apk_name

            apk_test_filepath = ""
            for path in test_apk_filepath_list:
                if apk_filename_without_extension in path and "-androidTest" in path:
                    apk_test_filepath = path

            self.apk_candidates.append(ApkCandidate(apk_filename,
                                                    apk_filepath,
                                                    apk_test_filename,
                                                    apk_test_filepath,
                                                    version_code))

    def _display_candidates(self):
        candidate_no = 0
        for apk_info in self.apk_candidates:
            candidate_no += 1
            Printer.system_message(self.TAG, "- Candidate no." + str(candidate_no) + " "
                                   + (Color.GREEN + "('can be used in test')" if apk_info.is_usable()
                                      else Color.RED + "('cannot be used in test - missing fields')"))
            Printer.system_message(self.TAG,
                                   "  Apk candidate name: " + Color.GREEN + str(apk_info.apk_name) + Color.END)
            Printer.system_message(self.TAG,
                                   "  Apk candidate path: " + Color.GREEN + str(apk_info.apk_path) + Color.END)
            Printer.system_message(self.TAG,
                                   "  Related test apk: " + Color.GREEN + str(apk_info.test_apk_name) + Color.END)
            Printer.system_message(self.TAG, "  Related test apk path: " + Color.GREEN + str(apk_info.test_apk_path)
                                   + Color.END)
            Printer.system_message(self.TAG, "  Version: " + Color.GREEN + str(apk_info.apk_version) + Color.END)

    def _get_usable_apk_candidate_for_latest_version(self):
        latest_apk_info = None
        latest_ver = -1
        for apk_info in self.apk_candidates:
            if apk_info.is_usable() and apk_info.apk_version > latest_ver:
                latest_apk_info = apk_info
                latest_ver = apk_info.apk_version
        return latest_apk_info
