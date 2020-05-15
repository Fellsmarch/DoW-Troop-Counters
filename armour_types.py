"""
Generates the armour type dictionaries to be saved to file.

- Generates a mapping from armour types to what troops have that armour type
- Generates a mapping from troops to what their armour type is

Harrison Cook
May 2020
"""
import csv
import logging

from file_handlers import create_and_check_path


def map_troops_to_armour_types(weapon_input_filename: str, armour_types: set):
    """
    Reads rows from a csv file and maps troops to the armour types they 
    have.

    :param weapon_input_filename: the weapon input csv filename
    :param armour_types: the set of armour types that exist in DoW
    :returns: a dictionary containing both mappings to/from armour types
    """
    weapon_input_path = create_and_check_path(weapon_input_filename, True)

    armour_types_dict = {}

    logging.debug("Loading weapon input csv file")
    with open(weapon_input_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        logging.debug("Done")

        for row in csv_reader:
            if row[0] in armour_types:
                troops_with_armour_type = format_troops(row[1].split(","))
                armour_types_dict[row[0]] = troops_with_armour_type

    return generate_armour_type_dicts(armour_types_dict)


def format_troops(troops_raw: list):
    """
    Formats a list of troops from make the name like it's corresponding 
    .lua file.

    :param troops_raw: a list of raw troop names
    :returns: a list of troop file names
    """
    troops = set()
    for troop in troops_raw:
        troop = troop.strip()
        troop = troop.replace(" ", "_")
        troop += ".lua"

        if troop != ".lua":
            troops.add(troop)

    return troops


def generate_armour_type_dicts(armour_types_dict: dict):
    """
    From the armour type > troop mapped dictionary, creates a 
    troop > armour type dictionary.

    :param armour_types_dict: the dictionary that maps armour types to troops
    :returns: a joint dictionary containing the input dictionary and a
                dictionary mapping troops to armour types
    """
    troops_to_armour_types_dict = {}

    for armour_type, troops in armour_types_dict.items():
        for troop in troops:
            if troop not in troops_to_armour_types_dict:
                troops_to_armour_types_dict[troop] = armour_type
    joint_dict = {"armourTypeToTroops": armour_types_dict,
                  "troopsToArmourType": troops_to_armour_types_dict}
    return joint_dict
