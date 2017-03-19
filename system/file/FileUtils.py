import os
import shutil
import codecs

from system.console import Printer
from settings import GlobalConfig

TAG = "FileManager:"


def create_file(folder, file_name, extension):
    directory = add_ending_slash(GlobalConfig.OUTPUT_DIR) + add_ending_slash(str(folder))
    file_path = clean_path(directory + str(file_name) + "." + extension)
    absolute_path = None
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
        open(file_path, "w")
        absolute_path = os.path.abspath(file_path)
        Printer.system_message(TAG, "Created file '" + str(absolute_path) + "'.")
    except Exception as e:
        Printer.error(TAG, "Unable to create file '" + file_path + "." + extension + ".")
        Printer.error(TAG, "Error message: " + str(e))
        quit()

    return absolute_path


def copy_file(file_to_copy, new_file):
    try:
        if os.path.isfile(file_to_copy):
            shutil.copy2(file_to_copy, new_file)
            Printer.system_message(TAG, "Copied file '" + str(file_to_copy) + "' to dir '" + str(new_file) + "'.")
    except Exception as e:
        Printer.error(TAG, "Unable to copy file '" + str(file_to_copy) + "'.")
        Printer.error(TAG, "Error message: " + str(e))
        quit()


def delete_file(file_to_delete):
    absolute_path = os.path.abspath(file_to_delete)
    try:
        if os.path.isfile(file_to_delete):
            os.unlink(file_to_delete)
            Printer.system_message(TAG, "Deleted file '" + str(file_to_delete) + "'.")
        elif os.path.isdir(file_to_delete):
            shutil.rmtree(file_to_delete)
            Printer.system_message(TAG, "Deleted directory '" + str(absolute_path) + "'.")
    except Exception as e:
        Printer.error(TAG, "Unable to delete file or directory '" + str(absolute_path) + "'.")
        Printer.error(TAG, "Error message: " + str(e))
        quit()


def clean_output_dir():
    directory = add_ending_slash(GlobalConfig.OUTPUT_DIR)

    for the_file in os.listdir(directory):
        file_path = os.path.join(directory, the_file)
        absolute_path = os.path.abspath(file_path)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
                Printer.system_message(TAG, "Deleted file '" + str(absolute_path) + "'.")
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
                Printer.system_message(TAG, "Deleted directory '" + str(absolute_path) + "'.")
        except Exception as e:
            Printer.error(TAG, "Unable to delete files in directory '" + directory + "'.")
            Printer.error(TAG, "Error message: " + str(e))
            quit()


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
