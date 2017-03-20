import os

from error.Exceptions import LauncherFlowInterruptedException

from settings import GlobalConfig
from settings.loader import ArgLoader
from settings.manifest.path.PathManifestModels import PathManifest

from system.console import Printer
from system.file.FileUtils import (
    clean_path,
    add_ending_slash
)

ANDROID_HOME_ENV = os.getenv('ANDROID_HOME')
ANDROID_SDK_HOME_ENV = os.getenv('ANDROID_SDK_HOME')

OUTPUT_DIR_DEFAULT = "output"

TAG = "PathsLoader:"


def init_paths():
    path_set_name = _load_path_set_name()
    path_manifest = _load_path_manifest()
    path_set = _load_path_set(path_manifest, path_set_name)

    _load_paths_to_global_settings(path_set)


def _load_path_set_name():
    path_set_name = ArgLoader.get_arg_loaded_by(ArgLoader.PATH_SET_PREFIX)
    if path_set_name is None:
        message = "No path set was selected. Launcher will quit."
        raise LauncherFlowInterruptedException(TAG, message)
    else:
        Printer.message_highlighted(TAG, "Selected path set: ", path_set_name)
    return path_set_name


def _load_path_manifest():
    path_manifest_dir = ArgLoader.get_arg_loaded_by(ArgLoader.PATH_MANIFEST_DIR_PREFIX)
    path_manifest = PathManifest(path_manifest_dir)
    Printer.message_highlighted(TAG, "Created PathManifest from file: ", path_manifest_dir)
    return path_manifest


def _load_path_set(path_manifest, path_set_name):
    if path_manifest.contains_set(path_set_name):
        Printer.system_message(TAG, "Path set '" + path_set_name + "' was found in PathManifest.")
        return path_manifest.get_set(path_set_name)
    else:
        message = "Invalid path set with name '{}' does not exist in PathManifest!"
        message = message.format(path_set_name)
        raise LauncherFlowInterruptedException(TAG, message)


def _load_paths_to_global_settings(path_set):
    GlobalConfig.SDK_DIR = add_ending_slash(clean_path((path_set.paths["sdk_dir"]).path_value))
    if GlobalConfig.SDK_DIR == "":
        Printer.system_message(TAG, "SDK path not set in PathManifest. "
                                    "Will use path set in env variable 'ANDROID_HOME'.")
        if ANDROID_HOME_ENV is None:
            message = "Env variable 'ANDROID_HOME' is not set. Launcher will quit."
            raise LauncherFlowInterruptedException(TAG, message)
        else:
            GlobalConfig.SDK_DIR = add_ending_slash(clean_path(ANDROID_HOME_ENV))
    Printer.message_highlighted(TAG, "Launcher will look for SDK at dir: ", GlobalConfig.SDK_DIR)

    GlobalConfig.AVD_DIR = add_ending_slash(clean_path((path_set.paths["avd_dir"]).path_value))
    if GlobalConfig.AVD_DIR == "":
        Printer.system_message(TAG, "AVD path not set in PathManifest. "
                                    "Will use path set in env variable 'ANDROID_SDK_HOME'.")
        if ANDROID_SDK_HOME_ENV is None:
            Printer.system_message(TAG, "Env variable 'ANDROID_SDK_HOME' is not set. "
                                        "Trying to recreate default path from user root.")
            GlobalConfig.AVD_DIR = add_ending_slash(clean_path("~")) + ".android"
    Printer.message_highlighted(TAG, "Launcher will look for AVD images at dir: ", GlobalConfig.AVD_DIR)

    GlobalConfig.OUTPUT_DIR = add_ending_slash(clean_path((path_set.paths["output_dir"]).path_value))
    if GlobalConfig.OUTPUT_DIR == "":
        Printer.system_message(TAG, "Output path not set in PathManifest. Default value will be used.")
        GlobalConfig.OUTPUT_DIR = OUTPUT_DIR_DEFAULT
    Printer.message_highlighted(TAG, "Launcher will generate log from tests in dir: ", GlobalConfig.OUTPUT_DIR)

    GlobalConfig.PROJECT_ROOT_DIR = add_ending_slash(clean_path((path_set.paths["project_root_dir"]).path_value))
    if GlobalConfig.PROJECT_ROOT_DIR == "":
        Printer.system_message(TAG, "Project root was not specified. This field is not obligatory.")
        Printer.error(TAG, "Warning: Without project root directory launcher will quit if no "
                           ".*apk files will be found in directory loaded from 'apk_dir' field of PathManifest.")
    else:
        Printer.message_highlighted(TAG, "Project root dir: ", GlobalConfig.PROJECT_ROOT_DIR)

    GlobalConfig.APK_DIR = add_ending_slash(clean_path((path_set.paths["apk_dir"]).path_value))
    if GlobalConfig.APK_DIR == "":
        message = "Directory with .*apk files was not found. Launcher will quit."
        raise LauncherFlowInterruptedException(TAG, message)
    Printer.message_highlighted(TAG, "Launcher will look for .*apk files in dir: ", GlobalConfig.APK_DIR)
