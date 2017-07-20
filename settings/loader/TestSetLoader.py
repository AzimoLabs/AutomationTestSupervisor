from error.Exceptions import LauncherFlowInterruptedException

from settings.loader import ArgLoader
from settings.manifest.models.TestManifestModels import TestManifest

from system.console import (
    Printer,
    Color
)

from system.file.FileUtils import (
    make_path_absolute
)

TAG = "TestSetLoader:"


def init_test_settings():
    test_set_name = _load_test_set_name()
    test_manifest = _load_manifest()
    test_list = _load_test_list(test_manifest)
    test_set = _load_test_set(test_manifest, test_set_name)

    return test_set, test_list


def _load_test_set_name():
    test_set_name = ArgLoader.get_arg_loaded_by(ArgLoader.TEST_SET_PREFIX)
    if test_set_name is None:
        message = "No test set inserted. Launcher will quit."
        raise LauncherFlowInterruptedException(TAG, message)
    else:
        Printer.system_message(TAG, "Selected test set: " + Color.GREEN + test_set_name + Color.BLUE + ".")
    return test_set_name


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


def _load_test_set(test_manifest, test_set_name):
    if test_manifest.contains_set(test_set_name):
        Printer.system_message(TAG, "Test set " + Color.GREEN + test_set_name + Color.BLUE
                               + " was found in TestManifest.")

        test_set = test_manifest.get_set(test_set_name)
        Printer.system_message(TAG, "Test set contains following package names: ")
        for package_name in test_set.set_package_names:
            Printer.system_message(TAG, "  * " + Color.GREEN + package_name + Color.BLUE)

        found_all_packages = True
        errors = ""
        for package_name in test_set.set_package_names:
            if not test_manifest.contains_package(package_name):
                found_all_packages = False
                errors += "\n              - Test package '" + package_name + "' was not found in TestManifest!"

        if found_all_packages:
            Printer.system_message(TAG, "All test packages from set " + Color.GREEN + test_set_name + Color.BLUE +
                                   " were found in TestManifest.")
        else:
            raise LauncherFlowInterruptedException(TAG, errors)
    else:
        message = "Test set '{}' not found in TestManifest. Launcher will quit."
        message = message.format(test_set_name)
        raise LauncherFlowInterruptedException(TAG, message)

    return test_set
