from settings.Settings import *
import glob
import os


def get_list_with_application_apk(apk_name_part_cleaned):
    apk_filenames = os.listdir(Settings.APK_DIR)

    application_apk_list = list()
    for apk_filename in apk_filenames:
        if apk_name_part_cleaned in apk_filename and "androidTest" not in apk_filename:
            application_apk_list.append(apk_filename)
    return application_apk_list


def get_list_with_application_apk_filepath(apk_name_part_cleaned):
    apk_absolute_paths = glob.glob(Settings.APK_DIR + "*")

    application_apk_filepath_list = list()
    for apk_path in apk_absolute_paths:
        if apk_name_part_cleaned in apk_path and "androidTest" not in apk_path:
            application_apk_filepath_list.append(apk_path)
    return application_apk_filepath_list


def get_list_with_test_apk(apk_name_part_cleaned):
    apk_filenames = os.listdir(Settings.APK_DIR)

    test_apk_list = list()
    for apk_filename in apk_filenames:
        if apk_name_part_cleaned in apk_filename and "androidTest" in apk_filename:
            test_apk_list.append(apk_filename)
    return test_apk_list


def get_list_with_test_apk_filepath(apk_name_part_cleaned):
    apk_absolute_paths = glob.glob(Settings.APK_DIR + "*")

    application_apk_filepath_list = list()
    for apk_path in apk_absolute_paths:
        if apk_name_part_cleaned in apk_path and "androidTest" in apk_path:
            application_apk_filepath_list.append(apk_path)
    return application_apk_filepath_list
