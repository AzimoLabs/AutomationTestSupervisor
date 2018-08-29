import time
import copy

from settings import GlobalConfig

from session.SessionModels import (
    SessionSummary,
    SessionDeviceSummary,
    SessionTimeSummary,
    SessionApkSummary,
    SessionTestSummary,
    SessionFlakinessCheckSummary
)

from system.file import FileUtils
from system.console import (
    Printer,
    Color
)

import os

TAG = "SessionLogger:"

session_log = SessionSummary()
session_log.device_summaries = dict()
session_log.time_summary = SessionTimeSummary()
session_log.apk_summary = SessionApkSummary()

session_log.test_summary = SessionTestSummary()
session_log.test_summary.test_number = 0
session_log.test_summary.test_passed = 0
session_log.test_summary.test_failed = 0

session_log.flakiness_summary = SessionFlakinessCheckSummary()


def _log_device(device_name):
    session_device_summary = session_log.device_summaries.get(device_name)

    if session_device_summary is None:
        session_device_summary = SessionDeviceSummary()
        session_device_summary.device_name = device_name

    session_log.device_summaries.update({device_name: session_device_summary})


def log_device_creation_start_time(device_name):
    _log_device(device_name)

    session_device_summary = session_log.device_summaries.get(device_name)

    if session_device_summary is None:
        session_device_summary = SessionDeviceSummary()

    if session_device_summary.creation_start_time is None:
        session_device_summary.creation_start_time = time.time()

    session_log.device_summaries.update({device_name: session_device_summary})


def log_device_creation_end_time(device_name):
    _log_device(device_name)
    session_device_summary = session_log.device_summaries.get(device_name)

    if session_device_summary is None:
        session_device_summary = SessionDeviceSummary()

    if session_device_summary.creation_end_time is None:
        session_device_summary.creation_end_time = time.time()
        _update_device_creation_time(session_device_summary)

    session_log.device_summaries.update({device_name: session_device_summary})


def _update_device_creation_time(session_device_summary):
    if session_device_summary.creation_start_time is not None and session_device_summary.creation_end_time is not None:
        session_device_summary.creation_time = \
            session_device_summary.creation_end_time - session_device_summary.creation_start_time


def log_device_launch_start_time(device_name):
    _log_device(device_name)
    session_device_summary = session_log.device_summaries.get(device_name)

    if session_device_summary is None:
        session_device_summary = SessionDeviceSummary()

    if session_device_summary.launch_start_time is None:
        session_device_summary.launch_start_time = time.time()

    session_log.device_summaries.update({device_name: session_device_summary})


def log_device_launch_end_time(device_name):
    _log_device(device_name)
    session_device_summary = session_log.device_summaries.get(device_name)

    if session_device_summary is None:
        session_device_summary = SessionDeviceSummary()

    if session_device_summary.launch_end_time is None:
        session_device_summary.launch_end_time = time.time()
        _update_device_launch_time(session_device_summary)

    session_log.device_summaries.update({device_name: session_device_summary})


def _update_device_launch_time(session_device_summary):
    if session_device_summary.launch_start_time is not None and session_device_summary.launch_end_time is not None:
        session_device_summary.launch_time = \
            session_device_summary.launch_end_time - session_device_summary.launch_start_time


def log_app_apk_install_start_time_on_device(device_name):
    _log_device(device_name)
    session_device_summary = session_log.device_summaries.get(device_name)

    if session_device_summary is None:
        session_device_summary = SessionDeviceSummary()

    if session_device_summary.apk_install_start_time is None:
        session_device_summary.apk_install_start_time = time.time()

    session_log.device_summaries.update({device_name: session_device_summary})


def log_app_apk_install_end_time_on_device(device_name):
    _log_device(device_name)
    session_device_summary = session_log.device_summaries.get(device_name)

    if session_device_summary is None:
        session_device_summary = SessionDeviceSummary()

    if session_device_summary.apk_install_end_time is None:
        session_device_summary.apk_install_end_time = time.time()
        _update_app_apk_install_time_on_device(session_device_summary)

    session_log.device_summaries.update({device_name: session_device_summary})


def _update_app_apk_install_time_on_device(session_device_summary):
    if session_device_summary.apk_install_start_time is not None and \
                    session_device_summary.apk_install_end_time is not None:
        session_device_summary.apk_install_time = \
            session_device_summary.apk_install_end_time - session_device_summary.apk_install_start_time


def log_test_apk_install_start_time_on_device(device_name):
    _log_device(device_name)
    session_device_summary = session_log.device_summaries.get(device_name)

    if session_device_summary is None:
        session_device_summary = SessionDeviceSummary()

    if session_device_summary.test_apk_install_start_time is None:
        session_device_summary.test_apk_install_start_time = time.time()

    session_log.device_summaries.update({device_name: session_device_summary})


def log_test_apk_install_end_time_on_device(device_name):
    _log_device(device_name)
    session_device_summary = session_log.device_summaries.get(device_name)

    if session_device_summary is None:
        session_device_summary = SessionDeviceSummary()

    if session_device_summary.test_apk_install_end_time is None:
        session_device_summary.test_apk_install_end_time = time.time()
        _update_test_apk_install_time_on_device(session_device_summary)

    session_log.device_summaries.update({device_name: session_device_summary})


def _update_test_apk_install_time_on_device(session_device_summary):
    if session_device_summary.test_apk_install_end_time is not None and \
                    session_device_summary.test_apk_install_start_time is not None:
        session_device_summary.test_apk_install_time = \
            session_device_summary.test_apk_install_end_time - session_device_summary.test_apk_install_start_time


def log_app_apk(app_apk_name):
    session_log.apk_summary.apk = app_apk_name


def log_test_apk(test_apk_name):
    session_log.apk_summary.test_apk = test_apk_name


def log_apk_version_code(version_code):
    session_log.apk_summary.version_code = version_code


def log_app_apk_build_start_time():
    session_log.apk_summary.apk_build_start_time = time.time()


def log_app_apk_build_end_time():
    session_log.apk_summary.apk_build_end_time = time.time()
    _update_app_apk_build_time()


def _update_app_apk_build_time():
    if session_log.apk_summary.apk_build_start_time is not None \
            and session_log.apk_summary.apk_build_end_time is not None:
        session_log.apk_summary.apk_build_time = session_log.apk_summary.apk_build_end_time - \
                                                 session_log.apk_summary.apk_build_start_time


def log_test_apk_build_start_time():
    if session_log.apk_summary.test_apk_build_start_time is None:
        session_log.apk_summary.test_apk_build_start_time = time.time()


def log_test_apk_build_end_time():
    if session_log.apk_summary.test_apk_build_end_time is None:
        session_log.apk_summary.test_apk_build_end_time = time.time()
        _update_test_apk_build_time()


def _update_test_apk_build_time():
    if session_log.apk_summary.test_apk_build_start_time is not None \
            and session_log.apk_summary.test_apk_build_end_time is not None:
        session_log.apk_summary.test_apk_build_time = session_log.apk_summary.test_apk_build_end_time - \
                                                      session_log.apk_summary.test_apk_build_start_time


def log_total_device_creation_start_time():
    if session_log.time_summary.total_device_creation_start_time is None:
        session_log.time_summary.total_device_creation_start_time = time.time()


def log_total_device_creation_end_time():
    if session_log.time_summary.total_device_creation_end_time is None:
        session_log.time_summary.total_device_creation_end_time = time.time()
        _update_total_device_creation_time()


def _update_total_device_creation_time():
    if session_log.time_summary.total_device_creation_start_time is not None \
            and session_log.time_summary.total_device_creation_end_time is not None:
        session_log.time_summary.total_device_creation_time = session_log.time_summary.total_device_creation_end_time \
                                                              - \
                                                              session_log.time_summary.total_device_creation_start_time


def log_total_device_launch_start_time():
    if session_log.time_summary.total_device_launch_start_time is None:
        session_log.time_summary.total_device_launch_start_time = time.time()


def log_total_device_launch_end_time():
    if session_log.time_summary.total_device_launch_end_time is None:
        session_log.time_summary.total_device_launch_end_time = time.time()
        _update_total_device_launch_time()


def _update_total_device_launch_time():
    if session_log.time_summary.total_device_launch_start_time is not None \
            and session_log.time_summary.total_device_launch_end_time is not None:
        session_log.time_summary.total_device_launch_time = session_log.time_summary.total_device_launch_end_time - \
                                                            session_log.time_summary.total_device_launch_start_time


def log_total_apk_build_start_time():
    if session_log.time_summary.total_apk_build_start_time is None:
        session_log.time_summary.total_apk_build_start_time = time.time()


def log_total_apk_build_end_time():
    if session_log.time_summary.total_apk_build_end_time is None:
        session_log.time_summary.total_apk_build_end_time = time.time()
        _update_total_apk_build_time()


def _update_total_apk_build_time():
    if session_log.time_summary.total_apk_build_start_time is not None \
            and session_log.time_summary.total_apk_build_end_time is not None:
        session_log.time_summary.total_apk_build_time = \
            session_log.time_summary.total_apk_build_end_time - session_log.time_summary.total_apk_build_start_time


def log_total_apk_install_start_time():
    if session_log.time_summary.total_apk_install_start_time is None:
        session_log.time_summary.total_apk_install_start_time = time.time()


def log_total_apk_install_end_time():
    if session_log.time_summary.total_apk_install_end_time is None:
        session_log.time_summary.total_apk_install_end_time = time.time()
        _update_total_apk_install_time()


def _update_total_apk_install_time():
    if session_log.time_summary.total_apk_install_start_time is not None \
            and session_log.time_summary.total_apk_install_end_time is not None:
        session_log.time_summary.total_apk_install_time = \
            session_log.time_summary.total_apk_install_end_time - session_log.time_summary.total_apk_install_start_time


def log_total_test_start_time():
    if session_log.time_summary.total_test_start_time is None:
        session_log.time_summary.total_test_start_time = time.time()


def log_total_test_end_time():
    if session_log.time_summary.total_test_end_time is None:
        session_log.time_summary.total_test_end_time = time.time()
        _update_total_test_time()


def _update_total_test_time():
    if session_log.time_summary.total_test_start_time is not None \
            and session_log.time_summary.total_test_end_time is not None:
        session_log.time_summary.total_test_time = \
            session_log.time_summary.total_test_end_time - session_log.time_summary.total_test_start_time


def log_total_rerun_start_time():
    if session_log.time_summary.total_rerun_start_time is None:
        session_log.time_summary.total_rerun_start_time = time.time()


def log_total_rerun_end_time():
    if session_log.time_summary.total_rerun_end_time is None:
        session_log.time_summary.total_rerun_end_time = time.time()
        _update_total_rerun_time()


def _update_total_rerun_time():
    if session_log.time_summary.total_rerun_start_time is not None \
            and session_log.time_summary.total_rerun_end_time is not None:
        session_log.time_summary.total_rerun_time = \
            session_log.time_summary.total_rerun_end_time - session_log.time_summary.total_rerun_start_time


def log_session_start_time():
    if session_log.time_summary.total_session_start_time is None:
        session_log.time_summary.total_session_start_time = time.time()


def log_session_end_time():
    if session_log.time_summary.total_session_end_time is None:
        session_log.time_summary.total_session_end_time = time.time()
        _update_total_session_time()


def _update_total_session_time():
    if session_log.time_summary.total_session_start_time is not None \
            and session_log.time_summary.total_session_end_time is not None:
        session_log.time_summary.total_session_time = \
            session_log.time_summary.total_session_end_time - session_log.time_summary.total_session_start_time


def increment_passed_tests():
    session_log.test_summary.test_passed += 1
    _update_test_number()
    _update_health_rate()


def increment_failed_tests():
    session_log.test_summary.test_failed += 1
    _update_test_number()
    _update_health_rate()


def _update_test_number():
    session_log.test_summary.test_number = session_log.test_summary.test_passed + session_log.test_summary.test_failed


def _update_health_rate():
    if session_log.test_summary.test_passed != 0 and session_log.test_summary.test_failed == 0:
        session_log.test_summary.health_rate = 1.00
    elif session_log.test_summary.test_passed == 0 and session_log.test_summary.test_failed != 0:
        session_log.test_summary.health_rate = 0.00
    elif session_log.test_summary.test_passed == 0 and session_log.test_summary.test_failed == 0:
        session_log.test_summary.health_rate = 1.00
    else:
        session_log.test_summary.health_rate = session_log.test_summary.test_passed / \
                                               session_log.test_summary.test_number


def update_flaky_candidate(test_summary):
    session_log.flakiness_summary.suspects.setdefault(test_summary.test_name, {
        "failed_count": 1,
        "passed_count": 0,
        "is_flaky": False
    })

    if test_summary.test_status == "success":
        session_log.flakiness_summary.suspects[test_summary.test_name]["passed_count"] += 1
        session_log.flakiness_summary.suspects[test_summary.test_name]["is_flaky"] = True
    else:
        session_log.flakiness_summary.suspects[test_summary.test_name]["failed_count"] += 1


def dump_session_summary():
    print_device_summaries()
    print_time_summary()
    print_apk_summary()
    print_test_summary()
    print_rerun_summary()


def print_device_summaries():
    if session_log.device_summaries:
        Printer.system_message(TAG, "Device details:")
        for key, device_summary in session_log.device_summaries.items():
            Printer.system_message(TAG, " - device " + Color.GREEN + device_summary.device_name + Color.BLUE + ":")

            if device_summary.creation_time is not None:
                Printer.system_message(TAG, "    * Creation time: " + Color.GREEN + "{:.2f}".format(
                    device_summary.creation_time) + Color.BLUE + " seconds.")

            if device_summary.launch_time is not None:
                Printer.system_message(TAG, "    * Launch time: " + Color.GREEN + "{:.2f}".format(
                    device_summary.launch_time) + Color.BLUE + " seconds.")

            if device_summary.apk_install_time is not None:
                Printer.system_message(TAG, "    * .*apk install time: " + Color.GREEN + "{:.2f}".format(
                    device_summary.apk_install_time) + Color.BLUE + " seconds.")

            if device_summary.test_apk_install_time is not None:
                Printer.system_message(TAG, "    * Test .*apk install time: " + Color.GREEN + "{:.2f}".format(
                    device_summary.test_apk_install_time) + Color.BLUE + " seconds.")


def print_time_summary():
    Printer.system_message(TAG, "Time details:")
    if session_log.time_summary.total_device_creation_time is not None:
        Printer.system_message(TAG, "  * Total device creation process took: " + Color.GREEN +
                               "{:.2f}".format(session_log.time_summary.total_device_creation_time) + Color.BLUE
                               + " seconds.")

    if session_log.time_summary.total_device_launch_time is not None:
        Printer.system_message(TAG, "  * Total device launch process took: " + Color.GREEN +
                               "{:.2f}".format(session_log.time_summary.total_device_launch_time) + Color.BLUE
                               + " seconds.")
    if session_log.time_summary.total_apk_build_time is not None:
        Printer.system_message(TAG, "  * Total .*apk build process took: " + Color.GREEN +
                               "{:.2f}".format(session_log.time_summary.total_apk_build_time) + Color.BLUE
                               + " seconds.")
    if session_log.time_summary.total_apk_install_time is not None:
        Printer.system_message(TAG, "  * Total .*apk installation process took: " + Color.GREEN +
                               "{:.2f}".format(session_log.time_summary.total_apk_install_time) + Color.BLUE
                               + " seconds.")
    if session_log.time_summary.total_test_time is not None:
        Printer.system_message(TAG, "  * Total test process took: " + Color.GREEN +
                               "{:.2f}".format(session_log.time_summary.total_test_time) + Color.BLUE + " seconds.")
    if session_log.time_summary.total_rerun_time is not None:
        Printer.system_message(TAG, "  * Total test re-run process took: " + Color.GREEN +
                               "{:.2f}".format(session_log.time_summary.total_rerun_time) + Color.BLUE + " seconds.")
    if session_log.time_summary.total_session_time is not None:
        Printer.system_message(TAG, "  * Total session time: " + Color.GREEN +
                               "{:.2f}".format(session_log.time_summary.total_session_time) + Color.BLUE + " seconds.")


def print_apk_summary():
    if session_log.apk_summary.apk is not None and session_log.apk_summary.apk_build_time is not None:
        Printer.system_message(TAG, ".*apk details:")
        Printer.system_message(TAG, "  * Application .*apk name: " + Color.GREEN + session_log.apk_summary.apk
                               + Color.BLUE + ".")

        if session_log.apk_summary.apk_build_time is not None:
            Printer.system_message(TAG, "  * Application .*apk build and scan time: " + Color.GREEN
                                   + "{:.2f}".format(session_log.apk_summary.apk_build_time) + Color.BLUE + " seconds.")

        if session_log.apk_summary.test_apk is not None:
            Printer.system_message(TAG, "  * Test .*apk name: " + Color.GREEN + session_log.apk_summary.test_apk
                                   + Color.BLUE + ".")

        if session_log.apk_summary.test_apk_build_time is not None:
            Printer.system_message(TAG, "  * Test .*apk build and scan time: " + Color.GREEN
                                   + "{:.2f}".format(session_log.apk_summary.test_apk_build_time) + Color.BLUE
                                   + " seconds.")

        if session_log.apk_summary.version_code is not None:
            Printer.system_message(TAG, "  * Version: " + Color.GREEN + str(session_log.apk_summary.version_code)
                                   + Color.BLUE + ".")


def print_test_summary():
    Printer.system_message(TAG, "Test details:")
    Printer.system_message(TAG, "  * Total number of test cases: " + Color.GREEN +
                           str(session_log.test_summary.test_number) + Color.BLUE + ".")
    Printer.system_message(TAG, "  * Tests passed: " + Color.GREEN + str(session_log.test_summary.test_passed)
                           + Color.BLUE + ".")
    Printer.system_message(TAG, "  * Tests failed: " + Color.GREEN + str(session_log.test_summary.test_failed)
                           + Color.BLUE + ".")
    if session_log.test_summary.health_rate is not None:
        Printer.system_message(TAG, "  * Health rate: " + Color.GREEN
                               + "{0:.2f}%".format(session_log.test_summary.health_rate * 100) + Color.BLUE + ".")


def print_rerun_summary():
    if GlobalConfig.SHOULD_RERUN_FAILED_TESTS:
        Printer.system_message(TAG, "Re-run details:")
        Printer.system_message(TAG, "  * from " + Color.GREEN + "{}".format(session_log.test_summary.test_failed)
                               + Color.BLUE + " failed test cases, each was started again " + Color.GREEN
                               + "{}".format(GlobalConfig.FLAKINESS_RERUN_COUNT) + Color.BLUE + " times:")

        for suspect, status in session_log.flakiness_summary.suspects.items():
            Printer.system_message(TAG, "   * (failed: " + Color.GREEN +
                                   "{}".format(status["failed_count"]) + Color.BLUE + ", passed: " + Color.GREEN
                                   + "{}".format(status["passed_count"]) + Color.BLUE + ", is_flaky: " + Color.GREEN
                                   + "{}".format(status["is_flaky"]) + Color.BLUE + ") {}".format(suspect))


def dump_saved_files_history():
    nothing_to_display = True

    if FileUtils.dir_exists(GlobalConfig.OUTPUT_AVD_LOG_DIR):
        nothing_to_display = False
        saved_avd_logs = FileUtils.list_files_in_dir(GlobalConfig.OUTPUT_AVD_LOG_DIR)
        Printer.system_message(TAG, "Directory " + Color.GREEN + str(GlobalConfig.OUTPUT_AVD_LOG_DIR)
                               + Color.BLUE + " (" + Color.GREEN + str(len(saved_avd_logs)) + " files" + Color.BLUE
                               + ")")
        for saved_file in FileUtils.list_files_in_dir(GlobalConfig.OUTPUT_AVD_LOG_DIR):
            Printer.system_message(TAG, "  * " + saved_file + ".")

    if FileUtils.dir_exists(GlobalConfig.OUTPUT_TEST_LOG_DIR):
        nothing_to_display = False
        saved_test_summaries = FileUtils.list_files_in_dir(GlobalConfig.OUTPUT_TEST_LOG_DIR)
        Printer.system_message(TAG, "Directory " + Color.GREEN + str(GlobalConfig.OUTPUT_TEST_LOG_DIR)
                               + Color.BLUE + " (" + Color.GREEN + str(len(saved_test_summaries)) + " files"
                               + Color.BLUE + ")")
        for saved_file in FileUtils.list_files_in_dir(GlobalConfig.OUTPUT_TEST_LOG_DIR):
            Printer.system_message(TAG, "  * " + saved_file + ".")

    if FileUtils.dir_exists(GlobalConfig.OUTPUT_TEST_LOGCAT_DIR):
        nothing_to_display = False
        saved_logcats_summaries = FileUtils.list_files_in_dir(GlobalConfig.OUTPUT_TEST_LOGCAT_DIR)
        Printer.system_message(TAG, "Directory " + Color.GREEN + str(GlobalConfig.OUTPUT_TEST_LOGCAT_DIR)
                               + Color.BLUE + " (" + Color.GREEN + str(len(saved_logcats_summaries)) + " files"
                               + Color.BLUE + ")")
        for saved_file in saved_logcats_summaries:
            Printer.system_message(TAG, "  * " + saved_file + ".")

    if GlobalConfig.SHOULD_RECORD_TESTS:
        if FileUtils.dir_exists(GlobalConfig.OUTPUT_TEST_RECORDINGS_DIR):
            nothing_to_display = False
            saved_recordings_summaries = FileUtils.list_files_in_dir(GlobalConfig.OUTPUT_TEST_RECORDINGS_DIR)
            Printer.system_message(TAG, "Directory " + Color.GREEN + str(GlobalConfig.OUTPUT_TEST_RECORDINGS_DIR)
                                   + Color.BLUE + " (" + Color.GREEN + str(len(saved_recordings_summaries))
                                   + " files" + Color.BLUE + ")")
            for saved_file in saved_recordings_summaries:
                Printer.system_message(TAG, "  * " + saved_file + ".")

    if nothing_to_display:
        Printer.system_message(TAG, "No files were saved during session.")


def save_session_summary():
    if GlobalConfig.OUTPUT_SUMMARY_LOG_DIR is not None and os.path.exists(GlobalConfig.OUTPUT_SUMMARY_LOG_DIR):
        session_log_json_dict = copy.deepcopy(session_log)
        session_log_json_dict.time_summary = vars(session_log.time_summary)
        session_log_json_dict.apk_summary = vars(session_log.apk_summary)
        session_log_json_dict.test_summary = vars(session_log.test_summary)
        session_log_json_dict.device_summaries = list()
        for device_name, device_summary in session_log.device_summaries.items():
            session_log_json_dict.device_summaries.append(vars(device_summary))
        session_log_json_dict.flakiness_summary = vars(session_log.flakiness_summary)
        session_log_json_dict = vars(session_log_json_dict)

        FileUtils.save_json_dict_to_json(GlobalConfig.OUTPUT_SUMMARY_LOG_DIR, session_log_json_dict, "session_summary")
