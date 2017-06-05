import time

from settings import GlobalConfig

from session.SessionModels import (
    SessionSummary,
    SessionDeviceSummary,
    SessionTimeSummary,
    SessionApkSummary,
    SessionTestSummary
)
from system.console import (
    Printer,
    Color
)

import os

TAG = "SessionLogger:"

session_log = SessionSummary()
session_log.device_summaries = list()
session_log.time_summary = SessionTimeSummary()
session_log.apk_summary = list()
session_log.test_summary = SessionTestSummary()


def log_total_device_launch_start_time():
    session_log.time_summary.total_device_launch_time = time.time()


def log_total_device_launch_end_time():
    if session_log.time_summary.total_device_launch_time is None:
        session_log.time_summary.total_device_launch_time = -1
    else:
        session_log.time_summary.total_device_launch_time = time.time() - \
                                                            session_log.time_summary.total_device_launch_time


def log_total_apk_build_start_time():
    session_log.time_summary.total_apk_build_time = time.time()


def log_total_apk_build_end_time():
    if session_log.time_summary.total_apk_build_time is None:
        session_log.time_summary.total_apk_build_time = -1
    else:
        session_log.time_summary.total_apk_build_time = time.time() - session_log.time_summary.total_apk_build_time


def log_total_apk_install_start_time():
    session_log.time_summary.total_apk_install_time = time.time()


def log_total_apk_install_end_time():
    if session_log.time_summary.total_apk_install_time is None:
        session_log.time_summary.total_apk_install_time = -1
    else:
        session_log.time_summary.total_apk_install_time = time.time() - session_log.time_summary.total_apk_install_time


def log_total_test_start_time():
    session_log.time_summary.total_test_time = time.time()


def log_total_test_end_time():
    if session_log.time_summary.total_test_time is None:
        session_log.time_summary.total_test_time = -1
    else:
        session_log.time_summary.total_test_time = time.time() - session_log.time_summary.total_test_time


def log_session_start_time():
    session_log.time_summary.total_session_time = time.time()


def log_session_end_time():
    if session_log.time_summary.total_session_time is None:
        session_log.time_summary.total_session_time = -1
    else:
        session_log.time_summary.total_session_time = time.time() - session_log.time_summary.total_session_time


def increment_passed_tests():
    if session_log.test_summary.test_passed is None:
        session_log.test_summary.test_passed = 0

    session_log.test_summary.test_passed += 1


def increment_failed_tests():
    if session_log.test_summary.test_failed is None:
        session_log.test_summary.test_failed = 0

    session_log.test_summary.test_failed += 1


def dump_session_summary():
    Printer.system_message(TAG, "Total device launch process took: " + Color.GREEN +
                           "{:.2f}".format(session_log.time_summary.total_device_launch_time) + Color.BLUE
                           + " seconds.")

    Printer.system_message(TAG, "Total .*apk build process took: " + Color.GREEN +
                           "{:.2f}".format(session_log.time_summary.total_apk_build_time) + Color.BLUE + " seconds.")

    Printer.system_message(TAG, "Total .*apk installation process took: " + Color.GREEN +
                           "{:.2f}".format(session_log.time_summary.total_apk_install_time) + Color.BLUE + " seconds.")

    Printer.system_message(TAG, "Total test process took: " + Color.GREEN +
                           "{:.2f}".format(session_log.time_summary.total_test_time) + Color.BLUE + " seconds.")

    Printer.system_message(TAG, "Total session time: " + Color.GREEN +
                           "{:.2f}".format(session_log.time_summary.total_session_time) + Color.BLUE + " seconds.")


def dump_saved_files_history():
    saved_test_summaries = os.listdir(GlobalConfig.OUTPUT_TEST_LOG_DIR)
    saved_logcats_summaries = os.listdir(GlobalConfig.OUTPUT_TEST_LOGCAT_DIR)
    saved_recordings_summaries = os.listdir(GlobalConfig.OUTPUT_TEST_RECORDINGS_DIR)

    Printer.system_message(TAG, "Directory: " + Color.GREEN + str(GlobalConfig.OUTPUT_TEST_LOG_DIR)
                           + Color.BLUE + ".")
    Printer.system_message(TAG, "Saved test summaries: (" + Color.GREEN + str(len(saved_test_summaries))
                           + " files" + Color.BLUE + ")")
    for saved_file in os.listdir(GlobalConfig.OUTPUT_TEST_LOG_DIR):
        Printer.system_message(TAG, "  * " + saved_file + ".")

    Printer.system_message(TAG, "Directory: " + Color.GREEN + str(GlobalConfig.OUTPUT_TEST_LOGCAT_DIR)
                           + Color.BLUE + ".")
    Printer.system_message(TAG, "Saved logcats: (" + Color.GREEN + str(len(saved_logcats_summaries))
                           + " files" + Color.BLUE + ")")
    for saved_file in saved_logcats_summaries:
        Printer.system_message(TAG, "  * " + saved_file + ".")

    if GlobalConfig.SHOULD_RECORD_TESTS:
        Printer.system_message(TAG, "Directory: " + Color.GREEN + str(GlobalConfig.OUTPUT_TEST_RECORDINGS_DIR)
                               + Color.BLUE + ".")
        Printer.system_message(TAG, "Saved recordings: (" + Color.GREEN + str(len(saved_recordings_summaries))
                               + " files" + Color.BLUE + ")")
        for saved_file in saved_recordings_summaries:
            Printer.system_message(TAG, "  * " + saved_file + ".")
