"""
Generates the troop data to be put into the database
then creates the database and puts that data into
the database
"""
from file_handlers import read_from_lua, create_and_check_path
from pathlib import Path

WEAPONS = None

def collate_troop_data(troops_config: dict, weapons_dict: dict, armour_types_dict: dict):
    """
    Collates the troop data from the given input directories.
    """
    global WEAPONS
    WEAPONS = weapons_dict
    troops_dict = {}
    for race_name in troops_config:
        race_troops_directory = troops_config[race_name]
        race_troops_dict = read_race_troops(race_troops_directory, armour_types_dict)
        troops_dict[race_name] = race_troops_dict

    return troops_dict


def read_race_troops(race_troops_directory: str, armour_types_dict: dict):
    """
    Reads all of a race's troop files in a directory, makes them
    into a dictionary containing all of troops, along with their
    names and what weapons they use.
    """
    race_troops_dict = {}
    race_troops_path = create_and_check_path(race_troops_directory, True)

    # For each file(path) in the race_troops_directory directory ending in .lua
    for file_path in race_troops_path.glob("*.lua"):
        lua_lines = read_from_lua(file_path)
        troop_file = get_name_from_file_path(file_path)
        
        troop_name, troop_weapons = get_troop_info(lua_lines)
        armour_types = armour_types_dict[troop_file] if troop_file in armour_types_dict else None
        race_troops_dict[troop_file] = {   
                    "display_name": troop_name,
                    "weapons": troop_weapons, 
                    "armour_types": armour_types, 
                    "troop_file": troop_file
                }

    # In theory this could also be due to no weapons being found in a troop's .lua file
    if len(race_troops_dict) < 1:
        raise Exception(f"No (valid) .lua files found in the troops directory ('{str(race_troops_path)}')")    

    return race_troops_dict


def get_troop_info(troop_lua_lines: list):
    """
    From a list of lua file lines, pulls out what weapons this
    troop uses and the name of the troop.
    """
    troop_name = None
    troop_weapons = set()

    for line in troop_lua_lines:
        key, value = get_lua_key_value_pair(line)
        troop_name = get_troop_name(line, key) or troop_name
        
        # If the value isn't a weapon or isn't a valid weapon file
        if not "weapon_table" in key or not value:
            continue

        troop_weapons.add(value)

    return troop_name, troop_weapons


def get_lua_key_value_pair(lua_key_value_str: str):
    """
    Gets a lua key:value pair from the full string
    """
    value_index = lua_key_value_str.find("=")
    key = get_lua_key(lua_key_value_str[:value_index])

    # If the value should be a weapon, get the value of object
    value = get_weapon_filename(lua_key_value_str[value_index + 2:])

    return key, value


def get_lua_key(lua_key_value_str: str):
    """
    Iterates over a lua key:value pair to find the last lua
    sub-key. For example: weapon_01 in ["weapon_table"]["weapon_01"]
    """
    key = ""
    key_start = lua_key_value_str.find("[")
    while key_start >= 0:
        key_end = lua_key_value_str.find("]", key_start)
        key += lua_key_value_str[key_start:key_end + 1]
        key_start = lua_key_value_str.find("[", key_end)

    return key


def get_troop_name(lua_line: str, lua_key: str):
    """
    Extracts the troop name from this line if present,
    else returns None.
    """
    troop_name = None
    # Pull out troop name from comment
    if "screen_name_id" in lua_key: 
        name_index = lua_line.find("--")
        # Check that comment of the name is there
        if name_index >= 0:
            troop_name = lua_line[name_index + 2:].strip()
    
    return troop_name
    

def get_weapon_filename(lua_value: str):
    """
    Formats a lua value (from a key:value pair) into a
    weapon filename if it is one, or None if it's another
    type of value.
    """
    lua_value = lua_value.strip()
    lua_value = lua_value.strip("[]()")

    file_index = lua_value.rfind("\\")
    lua_value = lua_value[file_index + 1:]

    if lua_value and not lua_value == "nil" and lua_value in WEAPONS:
        return lua_value
    else:
        return None


def get_name_from_file_path(file_path: Path):
    """
    Get's a troop's name from it's file path
    """
    file_path_str = str(file_path)
    name_start = file_path_str.rfind("\\")
    if name_start < 0:
        return file_path_str
    
    return file_path_str[name_start + 1:]#.replace(".lua", "")