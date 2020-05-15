"""
Generates the weapon data from the input csv to be put into the data 
files then saves that data to the specified file.

Harrison Cook
May 2020
"""
import csv
import sys
import logging

from file_handlers import create_and_check_path
from pathlib import Path


def collate_weapon_data(weapon_input_filename: str):
    """
    Collates the weapon data and armour types from the given input file.

    :param weapon_input_filename: the filename/path to the weapon input file
    :returns: (a dictionary of armour types and their associated troops,
                a dictionary of all weapons andtheir dps) 
    """
    weapon_input_path = create_and_check_path(weapon_input_filename, True)
    armour_types, weapon_rows = weapon_file_reader(weapon_input_path)
    weapons_dict = create_weapons_dict(armour_types, weapon_rows)

    return armour_types, weapons_dict


def weapon_file_reader(weapon_input_path: Path):
    """
    Reads weapon information and armour types from the weapon file.

    :param weapon_input_path: the Path to the weapon input file
    :returns: (a set of all armour types, a list of the weapon csv rows)
    :raises: a generic exception when the armour types cannot be found
    """
    logging.debug("Loading weapon input csv file")
    with open(weapon_input_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        logging.debug("Done")

        armour_types = None
        weapon_rows = []
        for line in csv_reader:
            # Find first header/damage_type line
            if not armour_types and line[0] == "File":
                armour_types = line[1:]

            # Skip other header/damage_type lines
            if ".rgd" not in line[0]:
                continue

            weapon_rows.append(line)

        if not armour_types:
            error = "Could not find header row (armour types) in weapon stats file"
            logging.error(error)
            raise Exception(error)

    return set(armour_types), weapon_rows


def create_weapons_dict(armour_types: set, weapon_rows: list):
    """
    Creates a dictionary of weapons, where the weapon filename are the 
    keys and the dictionary of weapon damages are the values.

    :param armour_types: the set of possbile armour types
    :param weapon_rows: a list of the weapon csv rows
    :returns: a dictionary of all weapons mapped to their damage against
                each armour type
    """
    weapons_dict = {}
    for weapon_row in weapon_rows:
        weapon_dict = get_weapon_dict(armour_types, weapon_row)
        weapons_dict.update(weapon_dict)

    return weapons_dict


def get_weapon_dict(armour_types: set, weapon_row: list):
    """
    Creates a weapon's stats dictionary by mapping the armour types
    values as keys to the weapon_row values as values.

    :param armour_types: the set of possbile armour types
    :param weapon_rows: a single weapon csv rows
    :returns: a dictionary of a single weapon mapped to it's damage
                against each armour type
    """
    # Replace file type since units reference .lua not .rgd
    weapon_file_name = weapon_row[0].replace(".rgd", ".lua")

    weapon_damages_list = [float(num) for num in weapon_row[1:]]

    # Maps the damage_type values (as dict keys) to the weapon damages (as dict values)
    weapon_damages = dict(zip(armour_types, weapon_damages_list))

    weapon_dict = {weapon_file_name: weapon_damages}

    return weapon_dict
