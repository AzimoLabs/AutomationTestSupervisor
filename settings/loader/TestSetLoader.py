from error.Exceptions import LauncherFlowInterruptedException

from settings.loader import ArgLoader
from settings.manifest.models.TestManifestModels import TestManifest, TestSet

from system.console import (
    Printer,
    Color
)

from system.file.FileUtils import (
    make_path_absolute
)

TAG = "TestSetLoader:"


def init_test_settings():
    test_set_names = _load_test_set_name()
    test_manifest = _load_manifest()
    test_list = _load_test_list(test_manifest)
    test_set = _load_test_set(test_manifest, test_set_names)

    return test_set, test_list


def _load_test_set_name():
    test_set_names = ArgLoader.get_arg_loaded_by(ArgLoader.TEST_SET_PREFIX)
    if test_set_names is None or len(test_set_names) == 0:
        message = "No test set inserted. Launcher will quit."
        raise LauncherFlowInterruptedException(TAG, message)
    else:
        Printer.system_message(TAG, "Selected test sets: ")
        for t_set_name in test_set_names:
            Printer.system_message(TAG, "  * " + Color.GREEN + t_set_name + Color.BLUE)
    return test_set_names


def _load_manifest():
    test_manifest_dir = make_path_absolute(ArgLoader.get_manifest_dir(ArgLoader.TEST_MANIFEST_DIR_KEY))

    if test_manifest_dir is None:
        message = ("TestManifest file directory was not found. Check if config_files_dir.json exists in root "
                   "of project. Otherwise check if it's linking to existing file.")
        raise LauncherFlowInterruptedException(TAG, message)
    else:
        test_manifest = TestManifest(test_manifest_dir)
        Printer.system_message(TAG, "Created TestManifest from file: " + Color.GREEN + test_manifest_dir + Color.BLUE
                               + ".")
    return test_manifest


def _load_test_list(test_manifest):
    if test_manifest.test_package_list:
        return test_manifest.test_package_list
    else:
        message = "There are no tests specified in TestManifest! Launcher will quit."
        raise LauncherFlowInterruptedException(TAG, message)


def _check_if_packages_exists(test_manifest, test_set_names):
    found_all_packages = True
    errors = ""
    for test_set_name in test_set_names:
        if test_manifest.contains_set(test_set_name):
            Printer.system_message(TAG, "Test set " + Color.GREEN + test_set_name + Color.BLUE
                                   + " was found in TestManifest. Contains following package names:")

            test_set = test_manifest.get_set(test_set_name)
            for package_name in test_set.set_package_names:
                Printer.system_message(TAG, "  * " + Color.GREEN + package_name + Color.BLUE)

            for package_name in test_set.set_package_names:
                if not test_manifest.contains_package(package_name):
                    found_all_packages = False
                    errors += "\n              - Test package '" + package_name + "' was not found in TestManifest!"
        else:
            message = "Test set '{}' not found in TestManifest. Launcher will quit."
            message = message.format(test_set_name)
            raise LauncherFlowInterruptedException(TAG, message)
    if found_all_packages:
        Printer.system_message(TAG, "All test packages were found in TestManifest.")
    else:
        raise LauncherFlowInterruptedException(TAG, errors)


def _pick_test_set(test_manifest, test_set_names):
    if len(test_set_names) > 1:
        Printer.system_message(TAG, "There were " + Color.GREEN + "{}".format(len(test_set_names)) + Color.BLUE
                               + " test sets passed. Merge will occur now.")

        test_set_dict = dict()
        test_set_dict["set_name"] = "merged"
        test_set_dict["apk_name_part"] = None
        test_set_dict["application_apk_assemble_task"] = None
        test_set_dict["test_apk_assemble_task"] = None
        test_set_dict["gradle_build_params"] = None
        test_set_dict["shard"] = None
        test_set_dict["set_package_names"] = set()

        config_compatible = True
        errors_tuples = set()

        for test_set_name in test_set_names:
            test_set = test_manifest.get_set(test_set_name)
            for other_test_set_name in test_set_names:
                other_test_set = test_manifest.get_set(other_test_set_name)

                if test_set.apk_name_part != other_test_set.apk_name_part:
                    config_compatible = False
                    errors_tuples.add((test_set_name, other_test_set_name, "apk_name_part"))
                else:
                    test_set_dict["apk_name_part"] = test_set.apk_name_part

                if test_set.application_apk_assemble_task != other_test_set.application_apk_assemble_task:
                    config_compatible = False
                    errors_tuples.add((test_set_name, other_test_set_name, "application_apk_assemble_task"))
                else:
                    test_set_dict["application_apk_assemble_task"] = test_set.application_apk_assemble_task

                if test_set.test_apk_assemble_task != other_test_set.test_apk_assemble_task:
                    config_compatible = False
                    errors_tuples.add((test_set_name, other_test_set_name, "test_apk_assemble_task"))
                else:
                    test_set_dict["test_apk_assemble_task"] = test_set.test_apk_assemble_task

                if test_set.gradle_build_params != other_test_set.gradle_build_params:
                    config_compatible = False
                    errors_tuples.add((test_set_name, other_test_set_name, "gradle_build_params"))
                else:
                    test_set_dict["gradle_build_params"] = test_set.gradle_build_params

                if test_set.shard != other_test_set.shard:
                    config_compatible = False
                    errors_tuples.add((test_set_name, other_test_set_name, "shard"))
                else:
                    test_set_dict["shard"] = test_set.shard

                for package in test_set.set_package_names:
                    test_set_dict["set_package_names"].add(package)

        if config_compatible:
            Printer.system_message(TAG,
                                   "All tests sets are compatible and were successfully merged. Including packages:")

            merged_test_set = TestSet(test_set_dict)
            for package_name in merged_test_set.set_package_names:
                Printer.system_message(TAG, "  * " + Color.GREEN + package_name + Color.BLUE)

            return merged_test_set
        else:
            error = ""
            for tset1, tset2, parameter_name in errors_tuples:
                error += "\n              - Test set '{}' and test set '{}' have incompatible ".format(tset1, tset2) \
                         + "config (on parameter: {}) and cannot be merged.".format(parameter_name)
            raise LauncherFlowInterruptedException(TAG, error)
    else:
        return test_manifest.get_set(test_set_names[0])

def _load_test_set(test_manifest, test_set_names):
    _check_if_packages_exists(test_manifest, test_set_names)
    return _pick_test_set(test_manifest, test_set_names)
