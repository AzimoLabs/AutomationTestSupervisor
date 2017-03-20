import os
import shutil
import codecs

from error.Exceptions import LauncherFlowInterruptedException

from system.console import Printer

from settings import GlobalConfig

TAG = "FileManager:"


def create_file(folder, file_name, extension):
    directory = add_ending_slash(GlobalConfig.OUTPUT_DIR) + add_ending_slash(str(folder))
    file_path = clean_path(directory + str(file_name) + "." + extension)

    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
        open(file_path, "w")
        absolute_path = os.path.abspath(file_path)
        Printer.system_message(TAG, "Created file '" + absolute_path + "'.")
    except Exception as e:
        message = "Unable to create file '{}.{}'. Error message: {}"
        message = message.format(file_path, extension, str(e))
        raise LauncherFlowInterruptedException(TAG, message)

    return absolute_path


def copy_file(file_to_copy, new_file):
    try:
        if os.path.isfile(file_to_copy):
            shutil.copy2(file_to_copy, new_file)
            Printer.system_message(TAG, "Copied file '" + file_to_copy + "' to dir '" + new_file + "'.")
    except Exception as e:
        message = "Unable to copy file '{}'. Error message: {}"
        message = message.format(file_to_copy, str(e))
        raise LauncherFlowInterruptedException(TAG, message)


def delete_file(file_to_delete):
    absolute_path = os.path.abspath(file_to_delete)

    try:
        if os.path.isfile(file_to_delete):
            os.unlink(file_to_delete)
            Printer.system_message(TAG, "Deleted file '" + file_to_delete + "'.")
        elif os.path.isdir(file_to_delete):
            shutil.rmtree(file_to_delete)
            Printer.system_message(TAG, "Deleted directory '" + absolute_path + "'.")
    except Exception as e:
        message = "Unable to delete file or directory '{}'. Error message: {}"
        message = message.format(absolute_path, str(e))
        raise LauncherFlowInterruptedException(TAG, message)


def clean_output_dir():
    directory = add_ending_slash(GlobalConfig.OUTPUT_DIR)

    for the_file in os.listdir(directory):
        file_path = os.path.join(directory, the_file)
        absolute_path = os.path.abspath(file_path)

        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
                Printer.system_message(TAG, "Deleted file '" + absolute_path + "'.")
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
                Printer.system_message(TAG, "Deleted directory '" + absolute_path + "'.")
        except Exception as e:
            message = "Unable to delete files in directory '{}'. Error message: {}"
            message = message.format(directory, str(e))
            raise LauncherFlowInterruptedException(TAG, message)


def output_dir_has_files():
    directory = add_ending_slash(GlobalConfig.OUTPUT_DIR)
    found_file = False

    for the_file in os.listdir(directory):
        file_path = os.path.join(directory, the_file)
        if os.path.isfile(file_path) or os.path.isdir(file_path):
            found_file = True

    return found_file


def clean_path(path):
    return codecs.getdecoder('unicode_escape')(os.path.expanduser(path))[0]


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
