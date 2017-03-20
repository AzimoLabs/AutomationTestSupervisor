from settings import GlobalConfig
from settings.loader import ArgLoader
from settings.manifest.test.TestManifestModels import TestManifest

from system.console import Printer

TAG = "TestSetLoader:"


def init_test_settings():
    test_set_name = _load_test_set_name()
    test_manifest = _load_manifest()
    test_list = _load_test_list(test_manifest)
    test_set = _load_test_set(test_manifest, test_set_name)

    _load_test_settings_to_global_config(test_manifest)

    return test_set, test_list


def _load_test_set_name():
    test_set_name = ArgLoader.get_arg_loaded_by(ArgLoader.TEST_SET_PREFIX)
    if test_set_name is None:
        Printer.error(TAG, "No test set inserted. Launcher will quit.")
        quit()
    else:
        Printer.message_highlighted(TAG, "Selected test set: ", test_set_name)
    return test_set_name


def _load_manifest():
    test_manifest_dir = ArgLoader.get_arg_loaded_by(ArgLoader.TEST_MANIFEST_DIR_PREFIX)
    test_manifest = TestManifest(test_manifest_dir)
    Printer.message_highlighted(TAG, "Created TestManifest from file: ", str(test_manifest_dir))
    return test_manifest


def _load_test_list(test_manifest):
    test_list = None
    if test_manifest.test_package_list:
        test_list = test_manifest.test_package_list
    else:
        Printer.error(TAG, "There are no tests specified in TestManifest! Launcher will quit.")
        quit()
    return test_list


def _load_test_set(test_manifest, test_set_name):
    test_set = None
    if test_manifest.contains_set(test_set_name):
        Printer.system_message(TAG, "Test set '" + test_set_name + "' was found in TestManifest.")
        test_set = test_manifest.get_set(test_set_name)
        Printer.message_highlighted(TAG, "Test set contains following package names: ",
                                    ",".join(
                                        "'" + package_name + "'" for package_name in test_set.set_package_names))

        found_all_packages = True
        for package_name in test_set.set_package_names:
            if not test_manifest.contains_package(package_name):
                found_all_packages = False
                Printer.error(TAG, "Test package '" + package_name + "' was not found in TestManifest!")

        if found_all_packages:
            Printer.system_message(TAG, "All test packages from set '" + test_set_name
                                   + "' were found in TestManifest.")
        else:
            quit()
    else:
        Printer.error(TAG, "Test set '" + test_set_name + "' not found in TestManifest. Launcher will quit.")
        quit()
    return test_set


def _load_test_settings_to_global_config(test_manifest):
    GlobalConfig.INSTRUMENTATION_RUNNER = test_manifest.instrumentation_runner
    if GlobalConfig.INSTRUMENTATION_RUNNER == "":
        Printer.error(TAG, "Instrumentation Runner was not set. "
                           "Test can't start without it. Launcher will quit.")
    else:
        Printer.message_highlighted(TAG, "Instrumentation Runner set to: ", GlobalConfig.INSTRUMENTATION_RUNNER)
