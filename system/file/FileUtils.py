import os
import shutil
import codecs
import json

from error.Exceptions import LauncherFlowInterruptedException

TAG = "FileUtils:"


def dir_exists(directory):
    return os.path.exists(directory)


def create_dir(directory):
    dir_path = clean_path(directory)

    try:
        os.makedirs(directory)
    except Exception as e:
        message = "Unable to create directory '{}'. Error message: {}"
        message = message.format(dir_path, str(e))
        raise LauncherFlowInterruptedException(TAG, message)

    return True


def clear_dir(directory):
    if os.listdir(directory):
        for the_file in os.listdir(directory):
            file_path = os.path.join(directory, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                message = "Unable to delete files in directory '{}'. Error message: {}"
                message = message.format(directory, str(e))
                raise LauncherFlowInterruptedException(TAG, message)

    return True


def create_file(directory, file_name, extension):
    file_path = clean_path(directory + str(file_name) + "." + extension)

    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
        open(file_path, "w")
    except Exception as e:
        message = "Unable to create file '{}.{}'. Error message: {}"
        message = message.format(file_path, extension, str(e))
        raise LauncherFlowInterruptedException(TAG, message)

    return True


def load_json(json_dir):
    json_dir = clean_path(json_dir)
    json_file = None

    try:
        json_file = open(json_dir, "r")
        json_data = json_file.read()
    except Exception as e:
        message = "Unable to open file '{}'. Error message: {}"
        message = message.format(json_dir, str(e))
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


def save_json_dict_to_json(directory, json_dict, file_name):
    extension = ".json"
    if extension not in file_name:
        file_name = file_name + extension

    file_path = clean_path(directory + str(file_name))

    output_file = None
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
        output_file = open(file_path, "w")
        absolute_path = os.path.abspath(file_path)

        json.dump(json_dict, output_file, indent=4, ensure_ascii=False)
    except Exception as e:
        message = "Unable to create file '{}'. Error message: {}"
        message = message.format(file_path, extension, str(e))
        raise LauncherFlowInterruptedException(TAG, message)
    finally:
        if output_file is not None and hasattr(output_file, "close"):
            output_file.close()

    return absolute_path


def clean_folder_only_dir(path):
    return remove_slash_pairs(add_starting_slash(add_ending_slash(clean_path(path))))


def clean_path(path):
    return codecs.getdecoder("unicode_escape")(os.path.expanduser(path))[0]


def add_starting_slash(path):
    if path != "" and path[0] != "/":
        return "/" + path
    else:
        return path


def add_ending_slash(path):
    if path != "" and path[len(path) - 1] != "/":
        return path + "/"
    else:
        return path


def remove_slash_pairs(path):
    return path.replace("//", "/")


def get_project_root():
    return os.path.abspath(os.path.dirname(__name__))
