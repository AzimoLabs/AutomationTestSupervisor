import os

from error.Exceptions import LauncherFlowInterruptedException
from settings import GlobalConfig
from settings.loader import ArgLoader
from settings.manifest.models.PathManifestModels import PathManifest
from system.console import (
    Printer,
    Color
)
from system.file.FileUtils import (
    clean_folder_only_dir
)

HOME = "~/"

ANDROID_HOME_ENV = os.getenv('ANDROID_HOME')
ANDROID_SDK_HOME_ENV = os.getenv('ANDROID_SDK_HOME')

OUTPUT_DIR_DEFAULT = os.path.abspath(os.path.dirname(__name__)) + "/output/"
OUTPUT_AVD_LOG_FOLDER_DEFAULT = "/avd_logs"
OUTPUT_TEST_LOG_FOLDER_DEFAULT = "/test_results"
OUTPUT_TEST_LOGCAT_FOLDER_DEFAULT = "/test_logcats"
OUTPUT_TEST_VIDEO_FOLDER_DEFAULT = "/recordings"
DEVICE_VIDEO_STORAGE_FOLDER_DEFAULT = "/sdcard/test_automation_recordings"

TAG = "PathsLoader:"


def init_paths():
    _display_manifest_source_info()

    path_set_name = _load_path_set_name()
    path_manifest = _load_path_manifest()
    path_set = _load_path_set(path_manifest, path_set_name)

    _load_paths_to_global_settings(path_set)


def _display_manifest_source_info():
    Printer.system_message(TAG,
                           "File used for locating manifest files: " + Color.GREEN
                           + ArgLoader.CONFIG_FILES_DIR_DEFAULT_DIR + Color.BLUE + ".")


def _load_path_set_name():
    path_set_name = ArgLoader.get_arg_loaded_by(ArgLoader.PATH_SET_PREFIX)
    if path_set_name is None:
        message = "No path set was selected. Launcher will quit."
        raise LauncherFlowInterruptedException(TAG, message)
    else:
        Printer.system_message(TAG, "Selected path set: " + Color.GREEN + path_set_name + Color.BLUE + ".")
    return path_set_name


def _load_path_manifest():
    path_manifest_dir = ArgLoader.get_manifest_dir(ArgLoader.PATH_MANIFEST_DIR_KEY)

    if path_manifest_dir is None:
        message = ("PathManifest file directory was not found. Check if config_files_dir.json exists in root "
                   "of project. Otherwise check if it's linking to existing file.")
        raise LauncherFlowInterruptedException(TAG, message)
    else:
        path_manifest = PathManifest(path_manifest_dir)
        Printer.system_message(TAG, "Created PathManifest from file: " + Color.GREEN + path_manifest_dir + Color.BLUE
                               + ".")
    return path_manifest


def _load_path_set(path_manifest, path_set_name):
    if path_manifest.contains_set(path_set_name):
        Printer.system_message(TAG, "Path set " + Color.GREEN + path_set_name + Color.BLUE
                               + " was found in PathManifest.")
        return path_manifest.get_set(path_set_name)
    else:
        message = "Invalid path set with name '{}' does not exist in PathManifest!"
        message = message.format(path_set_name)
        raise LauncherFlowInterruptedException(TAG, message)


def _load_paths_to_global_settings(path_set):
    GlobalConfig.SDK_DIR = clean_folder_only_dir((path_set.paths["sdk_dir"]).path_value)
    if GlobalConfig.SDK_DIR == "":
        Printer.system_message(TAG, "SDK path not set in PathManifest. Will use path set in env variable "
                               + Color.GREEN + "ANDROID_HOME" + Color.BLUE + ".")
        if ANDROID_HOME_ENV is None:
            message = "Env variable 'ANDROID_HOME' is not set. Launcher will quit."
            raise LauncherFlowInterruptedException(TAG, message)
        else:
            GlobalConfig.SDK_DIR = clean_folder_only_dir(ANDROID_HOME_ENV)
    Printer.system_message(TAG, "Launcher will look for SDK in dir: " + Color.GREEN + GlobalConfig.SDK_DIR
                           + Color.BLUE + ".")

    GlobalConfig.AVD_DIR = clean_folder_only_dir((path_set.paths["avd_dir"]).path_value)
    if GlobalConfig.AVD_DIR == "":
        Printer.system_message(TAG, "AVD path not set in PathManifest. "
                                    "Will use path set in env variable 'ANDROID_SDK_HOME'.")
        if ANDROID_SDK_HOME_ENV is None:
            Printer.system_message(TAG, "Env variable 'ANDROID_SDK_HOME' is not set. "
                                        "Trying to recreate default path from user root.")
            GlobalConfig.AVD_DIR = clean_folder_only_dir(HOME) + ".android"
    Printer.system_message(TAG, "Launcher will look for AVD images in dir: " + Color.GREEN + GlobalConfig.AVD_DIR
                           + Color.BLUE + ".")

    GlobalConfig.PROJECT_ROOT_DIR = clean_folder_only_dir((path_set.paths["project_root_dir"]).path_value)
    if GlobalConfig.PROJECT_ROOT_DIR == "":
        Printer.system_message(TAG, "Project root was not specified. This field is not obligatory.")
        Printer.error(TAG, "Warning: Without project root directory launcher will quit if no "
                           ".*apk files will be found in directory loaded from 'apk_dir' field of PathManifest.")
    else:
        Printer.system_message(TAG, "Project root dir: " + Color.GREEN + GlobalConfig.PROJECT_ROOT_DIR
                               + Color.BLUE + ".")

    GlobalConfig.APK_DIR = clean_folder_only_dir((path_set.paths["apk_dir"]).path_value)
    if GlobalConfig.APK_DIR == "":
        message = "Directory with .*apk files was not specified. Launcher will quit."
        raise LauncherFlowInterruptedException(TAG, message)
    Printer.system_message(TAG, "Launcher will look for .*apk files in dir: " + Color.GREEN + GlobalConfig.APK_DIR
                           + Color.BLUE + ".")

    GlobalConfig.OUTPUT_DIR = clean_folder_only_dir((path_set.paths["output_dir"]).path_value)
    if GlobalConfig.OUTPUT_DIR == "":
        Printer.system_message(TAG, "Output path not set in PathManifest. Default value will be used.")
        GlobalConfig.OUTPUT_DIR = OUTPUT_DIR_DEFAULT
    if not os.path.isabs(GlobalConfig.OUTPUT_DIR):
        message = "Path " + GlobalConfig.OUTPUT_DIR + " needs to be absolute!"
        raise LauncherFlowInterruptedException(TAG, message)
    Printer.system_message(TAG, "Launcher will generate log from tests in dir: " + Color.GREEN +
                           GlobalConfig.OUTPUT_DIR + Color.BLUE + ".")

    GlobalConfig.OUTPUT_AVD_LOG_DIR = clean_folder_only_dir(GlobalConfig.OUTPUT_DIR + OUTPUT_AVD_LOG_FOLDER_DEFAULT)
    if not os.path.isabs(GlobalConfig.OUTPUT_AVD_LOG_DIR):
        message = "Path " + GlobalConfig.OUTPUT_AVD_LOG_DIR + " needs to be absolute!"
        raise LauncherFlowInterruptedException(TAG, message)
    Printer.system_message(TAG, "Logs from AVD will be stored in dir: " + Color.GREEN + GlobalConfig.OUTPUT_AVD_LOG_DIR
                           + Color.BLUE + ".")

    GlobalConfig.OUTPUT_TEST_LOG_DIR = clean_folder_only_dir(GlobalConfig.OUTPUT_DIR + OUTPUT_TEST_LOG_FOLDER_DEFAULT)
    if not os.path.isabs(GlobalConfig.OUTPUT_TEST_LOG_DIR):
        message = "Path " + GlobalConfig.OUTPUT_TEST_LOG_DIR + " needs to be absolute!"
        raise LauncherFlowInterruptedException(TAG, message)
    Printer.system_message(TAG, "Logs from tests will be stored in dir: " + Color.GREEN +
                           GlobalConfig.OUTPUT_TEST_LOG_DIR + Color.BLUE + ".")

    GlobalConfig.OUTPUT_TEST_LOGCAT_DIR = clean_folder_only_dir(
        GlobalConfig.OUTPUT_DIR + OUTPUT_TEST_LOGCAT_FOLDER_DEFAULT)
    if not os.path.isabs(GlobalConfig.OUTPUT_TEST_LOGCAT_DIR):
        message = "Path " + GlobalConfig.OUTPUT_TEST_LOGCAT_DIR + " needs to be absolute!"
        raise LauncherFlowInterruptedException(TAG, message)
    Printer.system_message(TAG, "Logcat logs from tests will be stored in dir: " + Color.GREEN +
                           GlobalConfig.OUTPUT_TEST_LOGCAT_DIR + Color.BLUE + ".")

    GlobalConfig.OUTPUT_TEST_RECORDINGS_DIR = clean_folder_only_dir(
        GlobalConfig.OUTPUT_DIR + OUTPUT_TEST_VIDEO_FOLDER_DEFAULT)
    if not os.path.isabs(GlobalConfig.OUTPUT_TEST_RECORDINGS_DIR):
        message = "Path " + GlobalConfig.OUTPUT_TEST_RECORDINGS_DIR + " needs to be absolute!"
        raise LauncherFlowInterruptedException(TAG, message)
    Printer.system_message(TAG, "Recordings from tests will be stored in dir: " + Color.GREEN +
                           GlobalConfig.OUTPUT_TEST_RECORDINGS_DIR + Color.BLUE + ".")

    GlobalConfig.DEVICE_VIDEO_STORAGE_DIR = clean_folder_only_dir(DEVICE_VIDEO_STORAGE_FOLDER_DEFAULT)
    Printer.system_message(TAG, "Recordings will be stored on ROOT directory of test device storage in " + Color.GREEN
                           + GlobalConfig.DEVICE_VIDEO_STORAGE_DIR + Color.BLUE + " folder.")
