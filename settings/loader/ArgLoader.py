import argparse
import os

from system.file.FileUtils import (
    clean_path,
    get_project_root,
    load_json,
    add_ending_slash
)

TAG = "ArgLoader:"

CONFIG_FILES_DIR_DEFAULT_DIR = clean_path(add_ending_slash(get_project_root()) + "config_files_dir_default.json")
CONFIG_FILES_DIR_CUSTOM_DIR = clean_path(add_ending_slash(get_project_root()) + "config_files_dir.json")

LAUNCH_MANIFEST_DIR_KEY = "launch_manifest_path"
TEST_MANIFEST_DIR_KEY = "test_manifest_path"
AVD_MANIFEST_DIR_KEY = "avd_manifest_path"
PATH_MANIFEST_DIR_KEY = "path_manifest_path"

config_files_dir = None
loading_from_default_file = False

if os.path.isfile(CONFIG_FILES_DIR_CUSTOM_DIR):
    config_files_dir = load_json(CONFIG_FILES_DIR_CUSTOM_DIR)
    loading_from_default_file = False
elif os.path.isfile(CONFIG_FILES_DIR_DEFAULT_DIR):
    config_files_dir = load_json(CONFIG_FILES_DIR_DEFAULT_DIR)
    loading_from_default_file = True


def get_manifest_dir(key):
    if config_files_dir is None:
        return config_files_dir
    else:
        return config_files_dir[key]


LAUNCH_PLAN_DEFAULT = "default"
TEST_SET_DEFAULT = None
AVD_SET_DEFAULT = "default"
PATH_SET_DEFAULT = "default"

LAUNCH_PLAN_PREFIX = "-lplan"
TEST_SET_PREFIX = "-tset"
AVD_SET_PREFIX = "-aset"
PATH_SET_PREFIX = "-pset"

parser = argparse.ArgumentParser()
parser.add_argument(LAUNCH_PLAN_PREFIX,
                    type=str,
                    default=LAUNCH_PLAN_DEFAULT,
                    help="Name of launch plan specified in LaunchManifest.json.")

parser.add_argument(TEST_SET_PREFIX,
                    type=str,
                    default=TEST_SET_DEFAULT,
                    help="Name of test set specified in TestManifest.json.")

parser.add_argument(AVD_SET_PREFIX,
                    type=str,
                    default=AVD_SET_DEFAULT,
                    help="Name of AVD set specified in AvdManifest.json.")

parser.add_argument(PATH_SET_PREFIX,
                    type=str,
                    default=PATH_SET_DEFAULT,
                    help="Name of path set set specified in PathManifest.json.")

parser_args = parser.parse_args()


def get_arg_loaded_by(param):
    if param == LAUNCH_PLAN_PREFIX:
        return parser_args.lplan
    if param == TEST_SET_PREFIX:
        return parser_args.tset
    if param == AVD_SET_PREFIX:
        return parser_args.aset
    if param == PATH_SET_PREFIX:
        return parser_args.pset
    return None
