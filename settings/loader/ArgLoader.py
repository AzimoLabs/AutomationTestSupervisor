import argparse
#TODO USE ONLY ONE LOAD METHOD
TAG = "ArgLoader:"

LAUNCH_PLAN_PREFIX = "-lplan"
TEST_SET_PREFIX = "-tset"
AVD_SET_PREFIX = "-aset"
PATH_SET_PREFIX = "-pset"

LAUNCH_MANIFEST_DIR_PREFIX = "-ldir"
TEST_MANIFEST_DIR_PREFIX = "-tdir"
AVD_MANIFEST_DIR_PREFIX = "-adir"
PATH_MANIFEST_DIR_PREFIX = "-pdir"

LAUNCH_PLAN_DEFAULT = "default"
TEST_SET_DEFAULT = None
AVD_SET_DEFAULT = "default"
PATH_SET_DEFAULT = "default"

LAUNCH_MANIFEST_DIR_DEFAULT = "settings/manifest/launch/launchManifest.json"
TEST_MANIFEST_DIR_DEFAULT = "settings/manifest/test/testManifest.json"
AVD_MANIFEST_DIR_DEFAULT = "settings/manifest/avd/avdManifest.json"
PATH_MANIFEST_DIR_DEFAULT = "settings/manifest/path/pathManifest.json"

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

parser.add_argument(LAUNCH_MANIFEST_DIR_PREFIX,
                    type=str,
                    default=LAUNCH_MANIFEST_DIR_DEFAULT,
                    help="Absolute path to LaunchManifest.json.")

parser.add_argument(TEST_MANIFEST_DIR_PREFIX,
                    type=str,
                    default=TEST_MANIFEST_DIR_DEFAULT,
                    help="Absolute path to TestManifest.json.")

parser.add_argument(AVD_MANIFEST_DIR_PREFIX,
                    type=str,
                    default=AVD_MANIFEST_DIR_DEFAULT,
                    help="Absolute path to AvdManifest.json.")

parser.add_argument(PATH_MANIFEST_DIR_PREFIX,
                    type=str,
                    default=PATH_MANIFEST_DIR_DEFAULT,
                    help="Absolute path to PathManifest.json.")
parser_args = parser.parse_args()


def load_launch_plan():
    return parser_args.lplan


def load_test_set():
    return parser_args.tset


def load_avd_set():
    return parser_args.aset


def load_path_set():
    return parser_args.pset


def load_launch_manifest_dir():
    return parser_args.ldir


def load_test_manifest_dir():
    return parser_args.tdir


def load_avd_manifest_dir():
    return parser_args.adir


def load_path_manifest_dir():
    return parser_args.pdir
