from android.apk.ApkHelper import *
from android.apk.model.ApkCandidate import *
from console.Printer import *
import re

TAG = "ApkProvider:"


class ApkProvider:
    def __init__(self, aapt_controller):
        self.aapt_controller = aapt_controller
        self.apk_candidates = list()

        if os.path.isdir(Settings.APK_DIR):
            print_message(TAG, "Directory '" + Settings.APK_DIR + "' was found.")
        else:
            print_error(TAG, "Directory '" + Settings.APK_DIR + "' does not exist. Launcher will quit.")
            quit()

    def provide_apk(self, test_set):
        self._find_candidates(test_set)
        self._display_candidates()
        return self._get_usable_apk()

    def _find_candidates(self, test_set):
        apk_name_part_cleaned = test_set.apk_name_part.replace(".apk", "")
        print_message(TAG, "Checking '" + Settings.APK_DIR + "' directory for list of .*apk with names containing '"
                      + apk_name_part_cleaned + "':")

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
            print_message(TAG, "- Candidate no." + str(candidate_no) + " "
                          + (Color.GREEN + "('can be used in test')" if apk_info.is_usable()
                             else Color.RED + "('cannot be used in test - missing fields')"))
            print_message(TAG, "  Apk candidate name: " + Color.GREEN + str(apk_info.apk_name) + Color.END)
            print_message(TAG, "  Apk candidate path: " + Color.GREEN + str(apk_info.apk_path) + Color.END)
            print_message(TAG, "  Related test apk: " + Color.GREEN + str(apk_info.test_apk_name) + Color.END)
            print_message(TAG, "  Related test apk path: " + Color.GREEN + str(apk_info.test_apk_path) + Color.END)
            print_message(TAG, "  Version: " + Color.GREEN + str(apk_info.apk_version) + Color.END)

    def _get_usable_apk(self):
        latest_apk_info = None
        latest_ver = -1
        for apk_info in self.apk_candidates:
            if apk_info.is_usable() and apk_info.apk_version > latest_ver:
                latest_apk_info = apk_info
                latest_ver = apk_info.apk_version
        return latest_apk_info
