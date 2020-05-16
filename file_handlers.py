"""
A helper module for reading and writing files.

Harrison Cook
May 2020
"""
import json
import logging

from pathlib import Path


class PathNotFoundError(Exception):
    """
    An exception for when either the directory doesn't exist, or the
    file doesn't exist.
    """
    def __init__(self, message: str=None, path: str=None):
        """
        :param message: the message to display in the exception
        :param path: the string of the path that couldn't be found
        """
        if not message:
            path_str = f"({path}) " if path else ""
            message = f"The file or directory {path_str}was not found"
            logging.error(f"PathNotFoundError: {message}")
        super().__init__(message)


class CustomEncoder(json.JSONEncoder):
    """
    A custom JSON encoder allowing me to pass in sets with changing them
    in code and also DamageInfo objects (from generate_data.py).
    """
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        elif obj.__class__.__name__ == "DamageInfo":
            return {
                "troop_file": obj.troop_file,
                "weapon": obj.weapon,
                "damage": obj.damage
            }

        return json.JSONEncoder.default(self, obj)


def create_directories(path: str):
    """
    Creates directories leading to a path if they don't exist.

    :param path: the path to create directories to
    """

    last_dir = max(path.rfind("/"), path.rfind("\\"))

    if last_dir < 0:  # If we're already in the final directory
        return

    last_val = path[last_dir:]
    is_file = last_val.find(".") >= 0

    working_path = path[:last_dir] if is_file else path

    path_object = Path(working_path)
    path_object.mkdir(parents=True, exist_ok=True)


def create_and_check_path(path: str, reading: bool):
    """
    Creates a path object and checks that path exists.

    :param path: The path string
    :param reading: Whether or not we are trying to read the file
    :return: A Path object
    :raises PathNotFoundError: when the file or directory cannot be found
    """
    path_object = Path(path)
    if not path_object.exists():
        if reading:
            raise PathNotFoundError(path=path)

        create_directories(path)

    return path_object


def save_to_json(file_path: str, dict_to_save: dict):
    """
    Saves a given dictionary to a json file.

    :param file_path: the path to file to save to
    :dict_to_save: the data to save to file
    """
    file_path_object = create_and_check_path(file_path, False)

    try:
        logging.debug(f"Saving data to json file ({file_path})")

        with open(file_path_object, "w") as outfile:
            json.dump(dict_to_save, outfile, cls=CustomEncoder, indent=4)

        logging.debug("Done")
    except Exception as e:
        logging.error(f"Failed to save data to json file ({file_path}): {e}")
        raise e


def load_from_json(file_path: str, suppress_logging=False):
    """
    Reads from a given json file to a dictionary.

    :param file_path: the path to file to read from
    :return: the data read from the file as a dictionary
    """
    file_path_object = create_and_check_path(file_path, True)

    try:
        if not suppress_logging:
            logging.debug(f"Reading data from json file ({file_path})")
        with open(file_path_object, "r") as json_file:
            data = json.load(json_file)
            if not suppress_logging:
                logging.debug("Done")
            return data
    except Exception as e:
        if not suppress_logging:
            logging.error(f"Failed to load data from json file ({file_path}): {e}")
        raise e


def read_from_lua(file_path: str):
    """
    Reads from a given lua file to a list of lines.

    :param file_path: the path to file to read from
    :return: the data read from the file as a list
    """
    file_path_object = create_and_check_path(file_path, True)

    try:
        logging.debug(f"Reading data from lua file ({file_path})")
        with open(file_path_object, "r") as lua_file:
            lines = lua_file.readlines()
            logging.debug("Done")
            return lines
    except Exception as e:
        logging.error(f"Failed to read data from lua file ({file_path}): {e}")
        raise e
