from error.Exceptions import LauncherFlowInterruptedException

from settings.loader import ArgLoader
from settings.manifest.avd.AvdManifestModels import AvdManifest

from system.console import (
    Printer,
    Color
)

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
        Printer.system_message(TAG, "No AVD set selected. ""Currently available real devices will be used in test "
                                    "session.")
    else:
        Printer.system_message(TAG, "Selected avd set: " + Color.GREEN + avd_set_name + Color.BLUE + ".")
    return avd_set_name


def _load_avd_manifest():
    avd_manifest_dir = ArgLoader.get_arg_loaded_by(ArgLoader.AVD_MANIFEST_DIR_PREFIX)
    avd_manifest = AvdManifest(avd_manifest_dir)
    Printer.system_message(TAG, "Created AvdManifest from file: " + Color.GREEN + avd_manifest_dir + Color.BLUE + ".")
    return avd_manifest


def _load_avd_set(avd_manifest, avd_set_name):
    if avd_manifest.contains_set(avd_set_name):
        Printer.system_message(TAG, "AVD set " + Color.GREEN + avd_set_name + Color.BLUE + " was found in AvdManifest.")

        avd_set = avd_manifest.get_set(avd_set_name)
        Printer.system_message(TAG, "Requested AVD in set:")
        for requested_avd_schema in avd_set.avd_list:
            Printer.system_message(TAG, "    * " + Color.GREEN + requested_avd_schema.avd_name + Color.BLUE
                                   + " - instances num: " + Color.GREEN + str(requested_avd_schema.instances)
                                   + Color.BLUE + ".")
    else:
        message = "Invalid AVD set. Set '{}' does not exist in AvdManifest!"
        message = message.format(avd_set_name)
        raise LauncherFlowInterruptedException(TAG, message)

    return avd_manifest.get_set(avd_set_name)


def _load_avd_schema(avd_manifest, avd_set, avd_set_name):
    avd_schema_dict = avd_manifest.avd_schema_dict

    for avd in avd_set.avd_list:
        if avd_manifest.contains_schema(avd.avd_name):
            Printer.system_message(TAG, "AVD schema " + Color.GREEN + avd.avd_name + Color.BLUE
                                   + " was found in AvdManifest.")
        else:
            message = "Set '{}' requests usage of AVD schema with name '{}' which doesn't exists in AVD schema list."
            message = message.format(avd_set_name, avd.avd_name)
            raise LauncherFlowInterruptedException(TAG, message)

    return avd_schema_dict
