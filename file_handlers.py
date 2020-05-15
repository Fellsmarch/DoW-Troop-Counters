"""
Handles the reading and writing of files
"""
import json

from pathlib import Path


class PathNotFoundError(Exception):
    def __init__(self, message=None, path=None):
        if not message:
            path_str = f"({path}) " if path else ""
            message = f"The file or directory {path_str}was not found"
        super().__init__(message)


class CustomEncoder(json.JSONEncoder):
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
    Creates directories to a path if they don't exist
    """
    
    last_dir = max(path.rfind("/"), path.rfind("\\"))

    if last_dir < 0:
        return

    last_val = path[last_dir:]
    is_file = last_val.find(".") >= 0

    working_path = path[:last_dir] if is_file else path

    path_object = Path(working_path)
    path_object.mkdir(parents=True, exist_ok=True)


def create_and_check_path(path: str, reading: bool):
    """
    Creates a path object and checks that path exists.

    @param path: The path itself
    @poram reading: Whether or not we are trying to read the file
    @return: A Path object
    """
    path_object = Path(path)
    if not path_object.exists():
        if reading:
            raise PathNotFoundError(path=path)
        
        create_directories(path)

    return path_object


def save_to_json(file_path: str, dict_to_save: dict):
    """
    Saves a given dictionary to a file
    """
    file_path_object = create_and_check_path(file_path, False)
    with open(file_path_object, "w") as outfile:
        json.dump(dict_to_save, outfile, cls=CustomEncoder, indent=4)


def load_from_json(file_path: str):
    """
    Reads from a given json file to a dictionary
    """
    file_path_object = create_and_check_path(file_path, True)
    with open(file_path_object, "r") as json_file:
        data = json.load(json_file)
        return data


def read_from_lua(file_path: str):
    """
    Reads from a given lua file to a list of lines
    """
    file_path_object = create_and_check_path(file_path, True)
    with open(file_path_object, "r") as lua_file:
        lines = lua_file.readlines()
        return lines