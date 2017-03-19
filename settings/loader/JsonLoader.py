import os
import json

from system.file import FileUtils
from system.console import Printer


TAG = "JsonLoader:"


def load_json(json_dir):
    json_dir = FileUtils.clean_path(json_dir)
    json_dict = None
    json_file = None
    json_data = None

    try:
        json_file = open(json_dir, "r")
        json_data = json_file.read()
        Printer.system_message(TAG, "JSON file '" + os.getcwd() + "/" + json_dir + "' successfully loaded.")
    except Exception as e:
        Printer.error(TAG, "Unable to open file '"
                      + os.getcwd() + "/" + json_dir + "'.")
        Printer.error(TAG, "Error message: " + str(e))
        quit()
    finally:
        if json_file is not None and hasattr(json_file, "close"):
            json_file.close()

    try:
        json_dict = json.loads(json_data)
    except Exception as e:
        Printer.error(TAG, "Unable to parse JSON file '"
                      + os.getcwd() + "/" + json_dir + "'.")
        Printer.error(TAG, "Error message: " + str(e))
        quit()

    return json_dict
