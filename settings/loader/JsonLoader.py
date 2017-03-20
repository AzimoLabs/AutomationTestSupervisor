import os
import json

from error.Exceptions import LauncherFlowInterruptedException

from system.file import FileUtils
from system.console import Printer

TAG = "JsonLoader:"


def load_json(json_dir):
    json_dir = FileUtils.clean_path(json_dir)
    json_file = None

    try:
        json_file = open(json_dir, "r")
        json_data = json_file.read()
        Printer.system_message(TAG, "JSON file '" + os.getcwd() + "/" + json_dir + "' successfully loaded.")
    except Exception as e:
        message = "Unable to open file '{}/{}'. Error message: {}"
        message = message.format(os.getcwd(), json_dir, str(e))
        raise LauncherFlowInterruptedException(TAG, message)
    finally:
        if json_file is not None and hasattr(json_file, "close"):
            json_file.close()

    try:
        json_dict = json.loads(json_data)
    except Exception as e:
        message = "Unable to parse JSON file '{}/{}'. Error message: {}"
        message = message.format(os.getcwd(), json_dir, str(e))
        raise LauncherFlowInterruptedException(TAG, message)

    return json_dict
