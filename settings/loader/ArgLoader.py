from console.Printer import *
import re

TAG = "ArgLoader:"

LAUNCH_PLAN_PREFIX = "-lp"
TEST_SET_PREFIX = "-ts"
AVD_SET_PREFIX = "-as"
PATH_SET_PREFIX = "-ps"

LAUNCH_MANIFEST_DIR_PREFIX = "-lmdir"
TEST_MANIFEST_DIR_PREFIX = "-tmdir"
AVD_MANIFEST_DIR_PREFIX = "-amdir"
PATH_MANIFEST_DIR_PREFIX = "-pmdir"


def load_launch_plan(args, default):
    return _load_by_prefix(LAUNCH_PLAN_PREFIX, args, default)


def load_test_set(args, default):
    return _load_by_prefix(TEST_SET_PREFIX, args, default)


def load_avd_set(args, default):
    return _load_by_prefix(AVD_SET_PREFIX, args, default)


def load_path_set(args, default):
    return _load_by_prefix(PATH_SET_PREFIX, args, default)


def load_launch_manifest_dir(args, default):
    return _load_by_prefix(LAUNCH_MANIFEST_DIR_PREFIX, args, default)


def load_test_manifest_dir(args, default):
    return _load_by_prefix(TEST_MANIFEST_DIR_PREFIX, args, default)


def load_avd_manifest_dir(args, default):
    return _load_by_prefix(AVD_MANIFEST_DIR_PREFIX, args, default)


def load_plan_manifest_dir(args, default):
    return _load_by_prefix(PATH_MANIFEST_DIR_PREFIX, args, default)


# TODO: rewrite this with argparse
def _load_by_prefix(prefix, args, default):
    launch_cmd_args = ""
    for arg in args:
        if arg == args[0]:
            continue
        launch_cmd_args = " ".join((launch_cmd_args, arg))

    params = dict()
    params.update({"launch_plan": _extract_parameter(LAUNCH_PLAN_PREFIX, launch_cmd_args)})
    params.update({"test_set": _extract_parameter(TEST_SET_PREFIX, launch_cmd_args)})
    params.update({"avd_set": _extract_parameter(AVD_SET_PREFIX, launch_cmd_args)})
    params.update({"path_set": _extract_parameter(PATH_SET_PREFIX, launch_cmd_args)})
    params.update({"launch_manifest_dir": _extract_parameter(LAUNCH_MANIFEST_DIR_PREFIX, launch_cmd_args)})
    params.update({"test_manifest_dir": _extract_parameter(TEST_MANIFEST_DIR_PREFIX, launch_cmd_args)})
    params.update({"avd_manifest_dir": _extract_parameter(AVD_MANIFEST_DIR_PREFIX, launch_cmd_args)})
    params.update({"path_manifest_dir": _extract_parameter(PATH_MANIFEST_DIR_PREFIX, launch_cmd_args)})

    for param_name, param_value in params.items():
        if param_value is not None:
            launch_cmd_args = launch_cmd_args.replace(param_value, "", 1)
    launch_cmd_args = launch_cmd_args.replace(" ", "")

    if launch_cmd_args != "":
        print_error(TAG, "Unexpected particles in launch command: " + launch_cmd_args + ".")
        quit()

    for param_name, param_value in params.items():
        if param_value is None:
            params[param_name] = default

    if prefix == LAUNCH_PLAN_PREFIX:
        if params["launch_plan"] is not None:
            return params["launch_plan"].replace(prefix, "").strip()
    if prefix == TEST_SET_PREFIX:
        if params["test_set"] is not None:
            return params["test_set"].replace(prefix, "").strip()
    if prefix == AVD_SET_PREFIX:
        if params["avd_set"] is not None:
            return params["avd_set"].replace(prefix, "").strip()
    if prefix == PATH_SET_PREFIX:
        if params["path_set"] is not None:
            return params["path_set"].replace(prefix, "").strip()
    if prefix == LAUNCH_MANIFEST_DIR_PREFIX:
        if params["launch_manifest_dir"] is not None:
            return params["launch_manifest_dir"].replace(prefix, "").strip()
    if prefix == TEST_MANIFEST_DIR_PREFIX:
        if params["test_manifest_dir"] is not None:
            return params["test_manifest_dir"].replace(prefix, "").strip()
    if prefix == AVD_MANIFEST_DIR_PREFIX:
        if params["avd_manifest_dir"] is not None:
            return params["avd_manifest_dir"].replace(prefix, "").strip()
    if prefix == PATH_MANIFEST_DIR_PREFIX:
        if params["path_manifest_dir"] is not None:
            return params["path_manifest_dir"].replace(prefix, "").strip()

    return None


def _extract_parameter(prefix, launch_cmd_args):
    parameter_result = re.findall("(" + prefix + "\s[1-9a-zA-Z_-]+)", launch_cmd_args)
    if len(parameter_result) > 1:
        print_error(TAG, "Prefix " + prefix + " used more than once: " + str(parameter_result) + ".")
        quit()
    elif len(parameter_result) == 1:
        return str(parameter_result[0])
    else:
        return None
