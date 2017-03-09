import codecs
import os


def clean_path(path):
    return codecs.getdecoder('unicode_escape')(os.path.expanduser(path))[0]


def add_starting_slash(path):
    if path[0] != "/":
        return "/" + path
    else:
        return path


def add_ending_slash(path):
    if path[len(path) - 1] != "/":
        return path + "/"
    else:
        return path
