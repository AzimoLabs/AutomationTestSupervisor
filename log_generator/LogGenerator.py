import os
import datetime
import time

from log_generator.utils import (
    HtmlUtils,
    HtmlResultsUtils,
    HtmlSummaryUtils,
    HtmlLogcatUtils,
)

from log_generator.GeneratorModels import (
    LogPackage,
    Log
)

from settings import GlobalConfig

from system.file import FileUtils

TEST_STATUS_PASSED = "success"
TEST_STATUS_FAILED = "failure"

TEST_SUMMARY_HEADER_CELL = "Session summary"

TEST_SUMMARY_GENERAL_CELL = "General"
TEST_SUMMARY_SESSION_START_TIME_CELL = "Session start time:"
TEST_SUMMARY_SESSION_DURATION_CELL = "Session duration:"
TEST_SUMMARY_TOTAL_DEVICE_CREATION_DURATION_CELL = "Total device creation duration:"
TEST_SUMMARY_TOTAL_DEVICE_LAUNCH_DURATION_CELL = "Total device launch duration:"
TEST_SUMMARY_TOTAL_APK_BUILD_DURATION_CELL = "Total .apk build duration:"
TEST_SUMMARY_TOTAL_APK_INSTALL_DURATION_CELL = "Total .apk install duration:"
TEST_SUMMARY_TOTAL_TEST_SESSION_DURATION_CELL = "Total test session duration:"

TEST_SUMMARY_RESULTS_CELL = "Test results"
TEST_SUMMARY_PASSED_TESTS_CELL = "Passed tests:"
TEST_SUMMARY_FAILED_TESTS_CELL = "Failed tests:"

TEST_SUMMARY_APK_CELL = "Apk info"
TEST_SUMMARY_APK_UNDER_TEST_CELL = "Application under test .apk details"
TEST_SUMMARY_APK_TEST_CELL = "Test .apk details"
TEST_SUMMARY_APK_NAME_CELL = "Name:"
TEST_SUMMARY_APK_VERSION_CODE_CELL = "Version code:"
TEST_SUMMARY_APK_BUILD_DURATION_CELL = "Build duration:"

TEST_SUMMARY_DEVICES_CELL = "Devices used in session"
TEST_SUMMARY_DEVICE_CREATION_DURATION_CELL = "Device creation duration:"
TEST_SUMMARY_DEVICE_LAUNCH_DURATION_CELL = "Device launch duration:"
TEST_SUMMARY_DEVICE_APK_INSTALL_DURATION_CELL = ".apk install duration:"
TEST_SUMMARY_DEVICE_TEST_APK_INSTALL_DURATION_CELL = "Test .apk install duration:"

TEST_DURATION_CELL = "Test duration: {}"
TEST_DEVICE_CELL = "Test device: {}"
TEST_LOGCAT_CELL = "Logcat"
TEST_RECORDING_CELL = "Recordings: {}"

TEST_LOGCAT_LEVEL_DEBUG = "D"
TEST_LOGCAT_LEVEL_VERBOSE = "V"
TEST_LOGCAT_LEVEL_WARNING = "W"
TEST_LOGCAT_LEVEL_ERROR = "E"
TEST_LOGCAT_LEVEL_INFO = "I"

PREVIOUS_LOCATION = "../"
GENERATOR_STYLES_DIR = "/styles"
GENERATOR_SUMMARY_STYLE_FILE_NAME = "summary.css"
GENERATOR_LOGCAT_STYLE_FILE_NAME = "logcat.css"


def generate_logs(test_set):
    if test_set is not None and test_set.shard:
        generate_session_logs_for_shard_run()
    else:
        generate_session_logs_for_parallel_run()


def generate_session_logs_for_shard_run():
    _copy_styles()
    _create_summary_file()
    _create_logcats()


def generate_session_logs_for_parallel_run():
    _copy_styles()
    _create_summary_file()
    _create_logcats()


def _copy_styles():
    generator_styles_dir = FileUtils.clean_folder_only_dir(GlobalConfig.LOG_GENERATOR_DIR + GENERATOR_STYLES_DIR)
    FileUtils.copy(generator_styles_dir, GlobalConfig.OUTPUT_STYLES_FOLDER_DIR)


def _create_summary_file():
    file_dir = GlobalConfig.OUTPUT_DIR

    file_path = GlobalConfig.OUTPUT_INDEX_HTML_DIR
    filepath_parts = file_path.split("/")
    filename_with_extension = filepath_parts[len(filepath_parts) - 1]
    filename_parts = filename_with_extension.split(".")

    file_name = filename_parts[0]
    file_extension = filename_parts[1]

    FileUtils.create_file(file_dir, file_name, file_extension)

    with open(GlobalConfig.OUTPUT_INDEX_HTML_DIR, "w", encoding="utf-8") as html_file:
        html_content = _generate_summary_html()
        html_file.write(html_content)


def _create_logcats():
    logcat_html_path = GlobalConfig.OUTPUT_LOGCAT_HTML_DIR
    if not os.path.isdir(logcat_html_path):
        FileUtils.create_dir(logcat_html_path)

    logcats = load_logcats(GlobalConfig.OUTPUT_TEST_LOGCAT_DIR)
    for logcat_dict in logcats:
        file_dir = logcat_html_path
        file_name = logcat_dict["test_name"]
        file_extension = "html"
        file = "{}{}.{}".format(file_dir, file_name, file_extension)

        with open(file, "w", encoding="utf-8") as html_file:
            html_content = _generate_logcat_html(logcat_dict)
            html_file.write(html_content)


def _generate_summary_html():
    test_summary = load_summary(GlobalConfig.OUTPUT_SUMMARY_LOG_DIR)
    test_results = load_test_results(GlobalConfig.OUTPUT_TEST_LOG_DIR)
    log_packages = combine_logs(test_results)

    html_content = ""
    html_content += HtmlUtils.start_html()
    html_content += HtmlUtils.start_head()
    absolute_link_to_css = GlobalConfig.OUTPUT_STYLES_FOLDER_DIR + GENERATOR_SUMMARY_STYLE_FILE_NAME
    relative_link_to_css = make_absolute_path_relative_to_output_dir(absolute_link_to_css)
    html_content += HtmlUtils.link_css(relative_link_to_css)
    html_content += HtmlUtils.end_head()
    html_content += HtmlUtils.start_script()
    html_content += HtmlUtils.add_toggle_visibility_function_for_clean_package()
    html_content += HtmlUtils.add_toggle_visibility_function_for_package_with_fails()
    html_content += HtmlUtils.end_script()
    html_content += HtmlUtils.start_body()

    # container wrapper - start
    html_content += HtmlSummaryUtils.start_wrapper()

    # global header
    html_content += HtmlSummaryUtils.add_summary_header(TEST_SUMMARY_HEADER_CELL)

    # results - start table
    html_content += HtmlSummaryUtils.start_summary_table()

    # results - header
    html_content += HtmlSummaryUtils.add_summary_table_results_header(TEST_SUMMARY_RESULTS_CELL)

    # results - separator
    html_content += HtmlSummaryUtils.add_cell_separator()

    # results - health rate
    health_rate = _health_rate_to_display_format(test_summary["test_summary"]["health_rate"])
    html_content += HtmlSummaryUtils.add_summary_table_results_cell(health_rate)

    # results - passed tests
    html_content += HtmlSummaryUtils.start_summary_table_row()
    html_content += HtmlSummaryUtils.add_summary_table_results_passed_left(TEST_SUMMARY_PASSED_TESTS_CELL)
    passed_tests = _passed_tests_to_display_format(
        test_summary["test_summary"]["test_passed"], test_summary["test_summary"]["test_number"])
    html_content += HtmlSummaryUtils.add_summary_table_results_passed_right(passed_tests)
    html_content += HtmlSummaryUtils.end_row()

    # results - separator
    html_content += HtmlSummaryUtils.start_summary_table_row()
    html_content += HtmlSummaryUtils.add_cell_separator()
    html_content += HtmlSummaryUtils.end_row()

    # results - failed tests
    html_content += HtmlSummaryUtils.start_summary_table_row()
    html_content += HtmlSummaryUtils.add_summary_table_results_failed_left(TEST_SUMMARY_FAILED_TESTS_CELL)
    failed_tests = _passed_tests_to_display_format(
        test_summary["test_summary"]["test_failed"], test_summary["test_summary"]["test_number"])
    html_content += HtmlSummaryUtils.add_summary_table_results_failed_right(failed_tests)
    html_content += HtmlSummaryUtils.end_row()

    # results - end table
    html_content += HtmlSummaryUtils.end_table()

    # failed test list - start table
    failed_test_names = [test_result["test_name"] for test_result in test_results
                         if test_result["test_status"] != "success"]

    if failed_test_names:
        html_content += HtmlSummaryUtils.start_summary_failed_test_list_table()
        html_content += HtmlSummaryUtils.start_summary_failed_test_list_subtable()

        # failed test list - failed test rows
        displayed_tests = 0
        for failed_test_name in failed_test_names:
            html_content += HtmlSummaryUtils.start_summary_failed_test_row()

            counter = str(displayed_tests + 1) + ". "
            if displayed_tests % 2 == 0:
                html_content += HtmlSummaryUtils.add_summary_failed_test_row_cell_light(counter + failed_test_name)
            else:
                html_content += HtmlSummaryUtils.add_summary_failed_test_row_cell_dark(counter + failed_test_name)
            html_content += HtmlSummaryUtils.end_row()
            displayed_tests += 1

        # failed test list - end table
        html_content += HtmlSummaryUtils.end_row()
        html_content += HtmlSummaryUtils.end_table()
        html_content += HtmlSummaryUtils.add_cell_separator()

    # time summary - start table
    html_content += HtmlSummaryUtils.start_summary_table()

    # time summary - header
    html_content += HtmlSummaryUtils.add_summary_table_general_header(TEST_SUMMARY_GENERAL_CELL)

    # time summary - session start time
    html_content += HtmlSummaryUtils.start_summary_table_row()
    html_content += HtmlSummaryUtils.add_summary_table_general_cell_left(TEST_SUMMARY_SESSION_START_TIME_CELL)
    start_date = datetime.datetime.fromtimestamp(test_summary["time_summary"]["total_session_start_time"])
    html_content += HtmlSummaryUtils.add_summary_table_general_cell_right(start_date.strftime("%Y-%m-%d %H:%M:%S"))
    html_content += HtmlSummaryUtils.end_row()

    # time summary - separator
    html_content += HtmlSummaryUtils.start_summary_table_row()
    html_content += HtmlSummaryUtils.add_cell_separator()
    html_content += HtmlSummaryUtils.end_row()

    # time summary - session duration
    html_content += HtmlSummaryUtils.start_summary_table_row()
    html_content += HtmlSummaryUtils.add_summary_table_general_cell_left(TEST_SUMMARY_SESSION_DURATION_CELL)
    session_duration = _sec_to_display_format(test_summary["time_summary"]["total_session_time"])
    html_content += HtmlSummaryUtils.add_summary_table_general_cell_right(session_duration)
    html_content += HtmlSummaryUtils.end_row()

    # time summary - separator
    html_content += HtmlSummaryUtils.start_summary_table_row()
    html_content += HtmlSummaryUtils.add_cell_separator()
    html_content += HtmlSummaryUtils.end_row()

    # time summary - total device creation duration
    html_content += HtmlSummaryUtils.start_summary_table_row()
    html_content += HtmlSummaryUtils.add_summary_table_general_cell_left(
        TEST_SUMMARY_TOTAL_DEVICE_CREATION_DURATION_CELL)
    total_device_creation_duration = _sec_to_display_format(test_summary["time_summary"]["total_device_creation_time"])
    html_content += HtmlSummaryUtils.add_summary_table_general_cell_right(total_device_creation_duration)
    html_content += HtmlSummaryUtils.end_row()

    # time summary - separator
    html_content += HtmlSummaryUtils.start_summary_table_row()
    html_content += HtmlSummaryUtils.add_cell_separator()
    html_content += HtmlSummaryUtils.end_row()

    # time summary - total device launch duration
    html_content += HtmlSummaryUtils.start_summary_table_row()
    html_content += HtmlSummaryUtils.add_summary_table_general_cell_left(TEST_SUMMARY_TOTAL_DEVICE_LAUNCH_DURATION_CELL)
    total_device_launch_duration = _sec_to_display_format(test_summary["time_summary"]["total_device_launch_time"])
    html_content += HtmlSummaryUtils.add_summary_table_general_cell_right(total_device_launch_duration)
    html_content += HtmlSummaryUtils.end_row()

    # time summary - separator
    html_content += HtmlSummaryUtils.start_summary_table_row()
    html_content += HtmlSummaryUtils.add_cell_separator()
    html_content += HtmlSummaryUtils.end_row()

    # time summary - total apk build duration
    html_content += HtmlSummaryUtils.start_summary_table_row()
    html_content += HtmlSummaryUtils.add_summary_table_general_cell_left(TEST_SUMMARY_TOTAL_APK_BUILD_DURATION_CELL)
    total_apk_build_duration = _sec_to_display_format(test_summary["time_summary"]["total_apk_build_time"])
    html_content += HtmlSummaryUtils.add_summary_table_general_cell_right(total_apk_build_duration)
    html_content += HtmlSummaryUtils.end_row()

    # time summary - separator
    html_content += HtmlSummaryUtils.start_summary_table_row()
    html_content += HtmlSummaryUtils.add_cell_separator()
    html_content += HtmlSummaryUtils.end_row()

    # time summary - total apk install duration
    html_content += HtmlSummaryUtils.start_summary_table_row()
    html_content += HtmlSummaryUtils.add_summary_table_general_cell_left(TEST_SUMMARY_TOTAL_APK_INSTALL_DURATION_CELL)
    total_apk_install_duration = _sec_to_display_format(test_summary["time_summary"]["total_apk_install_time"])
    html_content += HtmlSummaryUtils.add_summary_table_general_cell_right(total_apk_install_duration)
    html_content += HtmlSummaryUtils.end_row()

    # time summary - separator
    html_content += HtmlSummaryUtils.start_summary_table_row()
    html_content += HtmlSummaryUtils.add_cell_separator()
    html_content += HtmlSummaryUtils.end_row()

    # time summary - total session duration
    html_content += HtmlSummaryUtils.start_summary_table_row()
    html_content += HtmlSummaryUtils.add_summary_table_general_cell_left(TEST_SUMMARY_TOTAL_TEST_SESSION_DURATION_CELL)
    total_apk_test_duration = _sec_to_display_format(test_summary["time_summary"]["total_test_time"])
    html_content += HtmlSummaryUtils.add_summary_table_general_cell_right(total_apk_test_duration)
    html_content += HtmlSummaryUtils.end_row()

    # time summary - end table
    html_content += HtmlSummaryUtils.end_table()
    html_content += HtmlSummaryUtils.add_cell_separator()

    # apk summary - start table
    html_content += HtmlSummaryUtils.start_summary_table()

    # apk summary - header
    html_content += HtmlSummaryUtils.add_summary_table_apk_header(TEST_SUMMARY_APK_CELL)

    # apk summary - start subtable - application under test
    html_content += HtmlSummaryUtils.start_summary_subtable()

    # apk summary - subheader
    html_content += HtmlSummaryUtils.add_summary_table_apk_subheader(TEST_SUMMARY_APK_UNDER_TEST_CELL)

    # apk summary - apk name
    html_content += HtmlSummaryUtils.start_summary_table_row()
    html_content += HtmlSummaryUtils.add_summary_table_apk_cell_left(TEST_SUMMARY_APK_NAME_CELL)
    apk_name = test_summary["apk_summary"]["apk"]
    html_content += HtmlSummaryUtils.add_summary_table_apk_cell_right(apk_name)
    html_content += HtmlSummaryUtils.end_table()

    # apk summary - subseparator
    html_content += HtmlSummaryUtils.start_summary_table_row()
    html_content += HtmlSummaryUtils.add_cell_subseparator()
    html_content += HtmlSummaryUtils.end_row()

    # apk summary - version code
    html_content += HtmlSummaryUtils.start_summary_table_row()
    html_content += HtmlSummaryUtils.add_summary_table_apk_cell_left(TEST_SUMMARY_APK_VERSION_CODE_CELL)
    apk_version_code = test_summary["apk_summary"]["version_code"]
    html_content += HtmlSummaryUtils.add_summary_table_apk_cell_right(apk_version_code)
    html_content += HtmlSummaryUtils.end_table()

    # apk summary - subseparator
    html_content += HtmlSummaryUtils.start_summary_table_row()
    html_content += HtmlSummaryUtils.add_cell_subseparator()
    html_content += HtmlSummaryUtils.end_row()

    # apk summary - build duration
    html_content += HtmlSummaryUtils.start_summary_table_row()
    apk_build_time = _sec_to_display_format(test_summary["apk_summary"]["apk_build_time"])
    html_content += HtmlSummaryUtils.add_summary_table_apk_cell_left(TEST_SUMMARY_APK_BUILD_DURATION_CELL)
    html_content += HtmlSummaryUtils.add_summary_table_apk_cell_right(apk_build_time)
    html_content += HtmlSummaryUtils.end_table()

    # apk summary - end subtable
    html_content += HtmlSummaryUtils.end_table()

    # apk summary - separator
    html_content += HtmlSummaryUtils.start_summary_table_row()
    html_content += HtmlSummaryUtils.add_cell_separator()
    html_content += HtmlSummaryUtils.end_row()

    # apk summary - start subtable - test apk
    html_content += HtmlSummaryUtils.start_summary_subtable()

    # apk summary - subheader
    html_content += HtmlSummaryUtils.add_summary_table_apk_subheader(TEST_SUMMARY_APK_TEST_CELL)

    # apk summary - apk name
    html_content += HtmlSummaryUtils.start_summary_table_row()
    html_content += HtmlSummaryUtils.add_summary_table_apk_cell_left(TEST_SUMMARY_APK_NAME_CELL)
    apk_name = test_summary["apk_summary"]["test_apk"]
    html_content += HtmlSummaryUtils.add_summary_table_apk_cell_right(apk_name)
    html_content += HtmlSummaryUtils.end_table()

    # apk summary - subseparator
    html_content += HtmlSummaryUtils.start_summary_table_row()
    html_content += HtmlSummaryUtils.add_cell_subseparator()
    html_content += HtmlSummaryUtils.end_row()

    # apk summary - version code
    html_content += HtmlSummaryUtils.start_summary_table_row()
    html_content += HtmlSummaryUtils.add_summary_table_apk_cell_left(TEST_SUMMARY_APK_VERSION_CODE_CELL)
    apk_version_code = test_summary["apk_summary"]["version_code"]
    html_content += HtmlSummaryUtils.add_summary_table_apk_cell_right(apk_version_code)
    html_content += HtmlSummaryUtils.end_table()

    # apk summary - subseparator
    html_content += HtmlSummaryUtils.start_summary_table_row()
    html_content += HtmlSummaryUtils.add_cell_subseparator()
    html_content += HtmlSummaryUtils.end_row()

    # apk summary - build duration
    html_content += HtmlSummaryUtils.start_summary_table_row()
    apk_build_time = _sec_to_display_format(test_summary["apk_summary"]["test_apk_build_time"])
    html_content += HtmlSummaryUtils.add_summary_table_apk_cell_left(TEST_SUMMARY_APK_BUILD_DURATION_CELL)
    html_content += HtmlSummaryUtils.add_summary_table_apk_cell_right(apk_build_time)
    html_content += HtmlSummaryUtils.end_table()

    # apk summary - end subtable
    html_content += HtmlSummaryUtils.end_table()

    # apk summary - end table
    html_content += HtmlSummaryUtils.end_table()
    html_content += HtmlSummaryUtils.add_cell_separator()

    # device summary - start table
    html_content += HtmlSummaryUtils.start_summary_table()

    # device summary - header
    html_content += HtmlSummaryUtils.add_summary_table_devices_header(TEST_SUMMARY_DEVICES_CELL)

    for device_dict in test_summary["device_summaries"]:
        # device summary - start subtable - device details
        html_content += HtmlSummaryUtils.start_summary_subtable()

        # device summary - subheader
        device_name = device_dict["device_name"]
        html_content += HtmlSummaryUtils.add_summary_table_devices_subheader(device_name)

        # device summary - device creation duration
        html_content += HtmlSummaryUtils.start_summary_table_row()
        creation_time = _sec_to_display_format(device_dict["creation_time"])
        html_content += HtmlSummaryUtils.add_summary_table_devices_cell_left(TEST_SUMMARY_DEVICE_CREATION_DURATION_CELL)
        html_content += HtmlSummaryUtils.add_summary_table_devices_cell_right(creation_time)
        html_content += HtmlSummaryUtils.end_row()

        # device summary - subseparator
        html_content += HtmlSummaryUtils.start_summary_table_row()
        html_content += HtmlSummaryUtils.add_cell_subseparator()
        html_content += HtmlSummaryUtils.end_row()

        # device summary - device launch duration
        html_content += HtmlSummaryUtils.start_summary_table_row()
        launch_time = _sec_to_display_format(device_dict["launch_time"])
        html_content += HtmlSummaryUtils.add_summary_table_devices_cell_left(TEST_SUMMARY_DEVICE_LAUNCH_DURATION_CELL)
        html_content += HtmlSummaryUtils.add_summary_table_devices_cell_right(launch_time)
        html_content += HtmlSummaryUtils.end_row()

        # device summary - subseparator
        html_content += HtmlSummaryUtils.start_summary_table_row()
        html_content += HtmlSummaryUtils.add_cell_subseparator()
        html_content += HtmlSummaryUtils.end_row()

        # device summary - apk install duration
        html_content += HtmlSummaryUtils.start_summary_table_row()
        apk_install_duration = _sec_to_display_format(device_dict["apk_install_time"])
        html_content += HtmlSummaryUtils.add_summary_table_devices_cell_left(
            TEST_SUMMARY_DEVICE_APK_INSTALL_DURATION_CELL)
        html_content += HtmlSummaryUtils.add_summary_table_devices_cell_right(apk_install_duration)
        html_content += HtmlSummaryUtils.end_row()

        # device summary - subseparator
        html_content += HtmlSummaryUtils.start_summary_table_row()
        html_content += HtmlSummaryUtils.add_cell_subseparator()
        html_content += HtmlSummaryUtils.end_row()

        # device summary - test apk install duration
        html_content += HtmlSummaryUtils.start_summary_table_row()
        test_apk_install_duration = _sec_to_display_format(device_dict["test_apk_install_time"])
        html_content += HtmlSummaryUtils.add_summary_table_devices_cell_left(
            TEST_SUMMARY_DEVICE_TEST_APK_INSTALL_DURATION_CELL)
        html_content += HtmlSummaryUtils.add_summary_table_devices_cell_right(test_apk_install_duration)
        html_content += HtmlSummaryUtils.end_row()

        # device summary - end subtable
        html_content += HtmlSummaryUtils.end_table()

    # device summary - end table
    html_content += HtmlSummaryUtils.end_table()
    html_content += HtmlSummaryUtils.add_cell_separator()

    # results from each test case
    for package in log_packages:

        passed_tests_num = 0
        failed_tests_num = 0
        for log in package.logs:
            if log.status == "success":
                passed_tests_num += 1
            else:
                failed_tests_num += 1

        header_text = package.name + " - (" + str(passed_tests_num) + " passed, " + str(failed_tests_num) + " failed)"
        package_header_code = HtmlResultsUtils.add_package_header(header_text)

        unique_id = "toggleable_package_" + "".join(str(time.time()).split("."))
        if failed_tests_num == 0:
            _add_toggleable_wrapped_id_to_summary_css(unique_id, "none")
            html_content += HtmlUtils.wrap_in_toggle_visibility_on_click_for_clean_package(
                package_header_code, unique_id)
        else:
            _add_toggleable_wrapped_id_to_summary_css(unique_id, "block")
            html_content += HtmlUtils.wrap_in_toggle_visibility_on_click_for_package_with_fails(
                package_header_code, unique_id)

        html_content += HtmlResultsUtils.add_test_case_separator()

        # package test results toggleable wrapper - start
        html_content += HtmlResultsUtils.start_test_package_wrapper(unique_id)

        for log in package.logs:
            if log.status == TEST_STATUS_PASSED:

                # passed test summary table
                html_content += HtmlResultsUtils.start_passed_test_table()
                html_content += HtmlResultsUtils.add_passed_test_header(log.name)

                html_content += HtmlResultsUtils.start_passed_test_row()
                html_content += HtmlResultsUtils.add_passed_test_cell(TEST_DURATION_CELL.format(log.duration))
                html_content += HtmlResultsUtils.add_passed_test_cell(TEST_DEVICE_CELL.format(log.device))
                html_content += HtmlResultsUtils.add_passed_test_cell(log.logcat)
                html_content += HtmlResultsUtils.add_passed_test_cell(log.recording)
                html_content += HtmlResultsUtils.end_row()

                html_content += HtmlResultsUtils.end_table()

            if log.status == TEST_STATUS_FAILED:
                html_content += HtmlResultsUtils.start_failed_table_wrapper()

                # failed test summary table
                html_content += HtmlResultsUtils.start_failed_test_table()
                html_content += HtmlResultsUtils.add_failed_test_header(log.name + " - FAILED")

                html_content += HtmlResultsUtils.start_failed_test_row()
                html_content += HtmlResultsUtils.add_failed_test_cell(TEST_DURATION_CELL.format(log.duration))
                html_content += HtmlResultsUtils.add_failed_test_cell(TEST_DEVICE_CELL.format(log.device))
                html_content += HtmlResultsUtils.add_failed_test_cell(log.logcat)
                html_content += HtmlResultsUtils.add_failed_test_cell(log.recording)
                html_content += HtmlResultsUtils.end_row()

                html_content += HtmlResultsUtils.end_table()

                # failed test error stacktrace
                html_content += HtmlResultsUtils.start_failed_test_error_table()

                error_messages = 0
                for error in log.error:
                    for line in error.split("\n"):
                        html_content += HtmlResultsUtils.start_failed_test_row()
                        if error_messages % 2 == 0:
                            html_content += HtmlResultsUtils.add_error_cell_light(line.replace("\t", "&emsp;&emsp;"))
                        else:
                            html_content += HtmlResultsUtils.add_error_cell_dark(line.replace("\t", "&emsp;&emsp;"))
                        html_content += HtmlResultsUtils.end_row()
                        error_messages += 1

                html_content += HtmlResultsUtils.end_table()
                html_content += HtmlResultsUtils.end_wrapper()

            html_content += HtmlResultsUtils.add_test_case_separator()

        # package test results toggleable wrapper - end
        html_content += HtmlResultsUtils.end_wrapper()

    # container wrapper - end
    html_content += HtmlSummaryUtils.end_wrapper()
    html_content += HtmlUtils.end_body()
    html_content += HtmlUtils.end_html()

    return html_content


def _add_toggleable_wrapped_id_to_summary_css(wrapper_id, value):
    with open(GlobalConfig.OUTPUT_STYLES_FOLDER_DIR + GENERATOR_SUMMARY_STYLE_FILE_NAME, "a", encoding="utf-8",
              errors="ignore") as summary_css:
        summary_css.write("\n\n")
        summary_css.write("#{}".format(wrapper_id) + " {\n")
        summary_css.write("    display: {};\n".format(value))
        summary_css.write("}")


def _generate_logcat_html(logcat_json_dict):
    html_content = ""

    html_content += HtmlUtils.start_html()
    html_content += HtmlUtils.start_head()
    absolute_link_to_css = GlobalConfig.OUTPUT_STYLES_FOLDER_DIR + GENERATOR_LOGCAT_STYLE_FILE_NAME
    relative_link_to_css = make_absolute_path_relative_to_output_dir(absolute_link_to_css, dirs_behind=1)
    html_content += HtmlUtils.link_css(relative_link_to_css)
    html_content += HtmlUtils.end_head()
    html_content += HtmlUtils.start_body()

    test_name = logcat_json_dict["test_name"]
    html_content += HtmlLogcatUtils.add_logcat_header(test_name)
    html_content += HtmlLogcatUtils.start_logcat_table()

    for line in logcat_json_dict["lines"]:
        level = line["level"] if not None else ""
        date = line["date"] if not None else ""
        time = line["time"] if not None else ""
        tag = line["tag"] if not None else ""
        message = line["text"] if not None else ""

        if level == TEST_LOGCAT_LEVEL_DEBUG:
            html_content += HtmlLogcatUtils.add_debug_row(date, time, tag, level, message)

        if level == TEST_LOGCAT_LEVEL_VERBOSE:
            html_content += HtmlLogcatUtils.add_verbose_row(date, time, tag, level, message)

        if level == TEST_LOGCAT_LEVEL_WARNING:
            html_content += HtmlLogcatUtils.add_warning_row(date, time, tag, level, message)

        if level == TEST_LOGCAT_LEVEL_ERROR:
            html_content += HtmlLogcatUtils.add_error_row(date, time, tag, level, message)

        if level == TEST_LOGCAT_LEVEL_INFO:
            html_content += HtmlLogcatUtils.add_info_row(date, time, tag, level, message)

    html_content += HtmlLogcatUtils.end_table()

    html_content += HtmlUtils.end_body()
    html_content += HtmlUtils.end_html()

    return html_content


def _sec_to_display_format(time_sec):
    if time_sec is None:
        return "0 sec"

    minutes = round(time_sec) // 60
    seconds = int(round(time_sec) - minutes * 60)

    time = ""
    if minutes > 0:
        time += "{} min, ".format(minutes)
    time += "{} sec".format(seconds)

    return time


def _health_rate_to_display_format(health_rate):
    if health_rate is None:
        return "100.00%"

    return "{0: .2f}%".format(health_rate * 100)


def _passed_tests_to_display_format(passed_tests, all_tests):
    if passed_tests is None or all_tests is None:
        return " --- "

    return "{} / {}".format(passed_tests, all_tests)


def _failed_tests_to_display_format(passed_tests, all_tests):
    if passed_tests is None or all_tests is None:
        return " --- "

    return "{} / {}".format(passed_tests, all_tests)


def load_summary(log_dir):
    files_in_summary_dir = FileUtils.list_files_in_dir(log_dir)

    if len(files_in_summary_dir) != 1:
        message = (
            "Something went wrong! There should be one file with name 'session_summary.json' in '" + log_dir
            + "' directory but " + str(len(files_in_summary_dir)) + " were found.")
        raise Exception(message)

    json_dict = FileUtils.load_json(log_dir + files_in_summary_dir[0])
    return json_dict


def load_test_results(log_dir):
    json_files = list()
    for file in FileUtils.list_files_in_dir(log_dir):
        if file.endswith(".json"):
            json_dict = FileUtils.load_json(log_dir + file)
            json_files.append(json_dict)
    return json_files


def load_logcats(log_dir):
    json_files = list()
    for file in FileUtils.list_files_in_dir(log_dir):
        if file.endswith(".json"):
            json_dict = FileUtils.load_json(log_dir + file)
            json_files.append(json_dict)
    return json_files


def combine_logs(test_results):
    test_packages = list()
    for test_result in test_results:
        log = Log()
        log.name = test_result["test_name"]
        log.package_name = extract_package_name(test_result["test_full_package"])
        log.device = test_result["device"]
        log.duration = calculate_duration(test_result["test_start_time"], test_result["test_end_time"])
        log.status = test_result["test_status"]
        log.error_type = ""
        log.error = test_result["error_messages"]
        log.logcat = create_link_to_logcat(test_result["test_name"], TEST_LOGCAT_CELL)
        log.recording = create_link_to_recording_file(test_result["test_name"])

        log_package_exists = False
        for test_package in test_packages:
            if test_package.name == log.package_name:
                log_package_exists = True
                test_package.logs.append(log)

        if not log_package_exists:
            package = LogPackage()
            package.name = log.package_name
            package.logs = list()
            package.logs.append(log)
            test_packages.append(package)

    return test_packages


def extract_package_name(full_package_name):
    parts = full_package_name.split(".")
    test_package = ".".join(parts[i] for i in range(0, len(parts) - 2))
    return test_package


def calculate_duration(test_start_time, test_end_time):
    duration_in_seconds = float(test_end_time - test_start_time) / 1000
    return "{:.2f} sec".format(duration_in_seconds)


def create_link_to_logcat(test_name, text):
    absolute_logcat_html_path = GlobalConfig.OUTPUT_LOGCAT_HTML_DIR + test_name + ".html"
    relative_logcat_html_path = make_absolute_path_relative_to_output_dir(absolute_logcat_html_path)
    return HtmlUtils.create_link_to_file(relative_logcat_html_path, text)


def create_link_to_recording_file(test_name):
    recordings_dir = GlobalConfig.OUTPUT_TEST_RECORDINGS_DIR

    links = ""
    recording_part = 0

    for path, subdirs, files in os.walk(recordings_dir):
        for f in files:
            absolute_recording_path = GlobalConfig.OUTPUT_TEST_RECORDINGS_DIR + f
            relative_recording_path = make_absolute_path_relative_to_output_dir(absolute_recording_path)
            if test_name in relative_recording_path:
                recording_part += 1
                filename = "p" + str(recording_part)
                links += HtmlUtils.create_link_to_file(relative_recording_path, filename)

    return TEST_RECORDING_CELL.format(links)


def make_absolute_path_relative_to_output_dir(path, dirs_behind=0):
    result_path = ""
    for i in range(dirs_behind):
        result_path += PREVIOUS_LOCATION
    return result_path + path.replace(GlobalConfig.OUTPUT_DIR, "")
