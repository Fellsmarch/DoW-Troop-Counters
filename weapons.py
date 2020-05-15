"""
Generates the weapon data to be put into the database
then creates the database and puts that data into
the database
"""
import csv
import sys

from file_handlers import create_and_check_path
from pathlib import Path


def collate_weapon_data(weapon_input_filename: str):
    """
    Collates the weapon data from the given input file
    and saves it.
    """
    weapon_input_path = create_and_check_path(weapon_input_filename, True)
    armour_types, weapon_rows = weapon_file_reader(weapon_input_path)
    weapons_dict = create_weapons_dict(armour_types, weapon_rows)

    return armour_types, weapons_dict


def weapon_file_reader(weapon_input_path: Path):
    with open(weapon_input_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")

        armour_types = None
        weapon_rows = []
        for line in csv_reader:
            # Find first header/damage_type line
            if not armour_types and line[0] == "File":
                armour_types = line[1:]

            # Skip other header/damage_type lines
            if ".rgd" not in line[0]: continue

            weapon_rows.append(line)

        if not armour_types:
            raise Exception("Could not find header row (armour types) in weapon stats file")

    return set(armour_types), weapon_rows


def create_weapons_dict(armour_types: list, weapon_rows: list):
    """
    Creates a dictionary of weapons, where the weapon filename
    are the keys and the dictionary of weapon damages are the
    values
    """
    weapons_dict = {}
    for weapon_row in weapon_rows:
        weapon_dict = get_weapon_dict(armour_types, weapon_row)
        weapons_dict.update(weapon_dict)

    return weapons_dict


def get_weapon_dict(armour_types: list, weapon_row: list):
    """
    Creates a weapon's stats dictionary by mapping the armour types
    values as keys to the weapon_row values as values.
    """ 
    # Replace file type since units reference .lua not .rgd
    weapon_file_name = weapon_row[0].replace(".rgd", ".lua")

    weapon_damages_list = [float(num) for num in weapon_row[1:]]

    # Maps the damage_type values (as dict keys) to the weapon damages (as dict values)
    weapon_damages = dict(zip(armour_types, weapon_damages_list))

    weapon_dict = {weapon_file_name: weapon_damages}

    return weapon_dict
