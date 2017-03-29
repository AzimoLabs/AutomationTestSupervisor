import re
import os

from . import ApkHelper
from .ApkModels import ApkCandidate

from settings import GlobalConfig

from system.file import FileUtils
from system.console import (
    Printer,
    Color
)


class ApkProvider:
    TAG = "ApkProvider:"

    def __init__(self, aapt_controller):
        self.aapt_controller = aapt_controller
        self.apk_candidates = list()
        self._create_apk_dir_if_not_exists()

    def _create_apk_dir_if_not_exists(self):
        if os.path.isdir(GlobalConfig.APK_DIR):
            Printer.system_message(self.TAG, "Directory '" + GlobalConfig.APK_DIR + "' was found.")
        else:
            Printer.system_message(self.TAG, "Directory '" + GlobalConfig.APK_DIR + "' not found. Creating...")
            FileUtils.create_dir(GlobalConfig.APK_DIR)

    def provide_apk(self, test_set):
        self._find_candidates(test_set)
        self._display_candidates()
        return self._get_usable_apk_candidate_for_latest_version()

    def _find_candidates(self, test_set):
        name_part = test_set.apk_name_part.replace(".apk", "")
        Printer.system_message(self.TAG,
                               "Checking '" + GlobalConfig.APK_DIR + "' directory for .*apk list with names " +
                               "containing '" + name_part + "':")

        app_apk_list = ApkHelper.get_list_with_application_apk(name_part, GlobalConfig.APK_DIR)
        app_apk_filepath_list = ApkHelper.get_list_with_application_apk_filepath(name_part, GlobalConfig.APK_DIR)
        test_apk_list = ApkHelper.get_list_with_test_apk(name_part, GlobalConfig.APK_DIR)
        test_apk_filepath_list = ApkHelper.get_list_with_test_apk_filepath(name_part, GlobalConfig.APK_DIR)

        for apk in app_apk_list:
            apk_filename = apk
            apk_filename_without_extension = apk_filename.replace(".apk", "")

            apk_filepath = ""
            for path in app_apk_filepath_list:
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
