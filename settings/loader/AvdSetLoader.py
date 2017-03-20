from error.Exceptions import LauncherFlowInterruptedException

from settings.loader import ArgLoader
from settings.manifest.avd.AvdManifestModels import AvdManifest

from system.console import Printer

TAG = "AvdSetLoader:"


def init_avd_settings():
    avd_set_name = _load_avd_set_name()
    avd_manifest = _load_avd_manifest()

    avd_set = None
    avd_schema_dict = None

    if avd_set_name != ArgLoader.AVD_SET_DEFAULT:
        avd_set = _load_avd_set(avd_manifest, avd_set_name)
        avd_schema_dict = _load_avd_schema(avd_manifest, avd_set, avd_set_name)

    return avd_set, avd_schema_dict


def _load_avd_set_name():
    avd_set_name = ArgLoader.get_arg_loaded_by(ArgLoader.AVD_SET_PREFIX)

    if avd_set_name is None:
        Printer.system_message(TAG, "No AVD set selected. "
                                    "Currently available real devices will be used in test session.")
    else:
        Printer.message_highlighted(TAG, "Selected avd set: ", avd_set_name)
    return avd_set_name


def _load_avd_manifest():
    avd_manifest_dir = ArgLoader.get_arg_loaded_by(ArgLoader.AVD_MANIFEST_DIR_PREFIX)
    avd_manifest = AvdManifest(avd_manifest_dir)
    Printer.message_highlighted(TAG, "Created AvdManifest from file: ", avd_manifest_dir)
    return avd_manifest


def _load_avd_set(avd_manifest, avd_set_name):
    if avd_manifest.contains_set(avd_set_name):
        Printer.system_message(TAG, "AVD set '" + avd_set_name + "' was found in AvdManifest.")
    else:
        message = "Invalid AVD set. Set '{}' does not exist in AvdManifest!"
        message = message.format(avd_set_name)
        raise LauncherFlowInterruptedException(TAG, message)

    return avd_manifest.get_set(avd_set_name)


def _load_avd_schema(avd_manifest, avd_set, avd_set_name):
    avd_schema_dict = avd_manifest.avd_schema_dict

    for avd in avd_set.avd_list:
        if avd_manifest.contains_schema(avd.avd_name):
            Printer.system_message(TAG, "AVD schema '" + avd.avd_name + "' found in AvdManifest.")
        else:
            message = "Set '{}' requests usage of AVD schema with name '{}' which doesn't exists in AVD schema list."
            message = message.format(avd_set_name, avd.avd_name)
            raise LauncherFlowInterruptedException(TAG, message)

    return avd_schema_dict
