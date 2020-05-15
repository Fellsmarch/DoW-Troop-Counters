"""
Creates a mapping between armour types and what troops
have that armour type
"""
import csv

from file_handlers import create_and_check_path


def map_troops_to_armour_types(weapon_input_filename: str, armour_types: set):
    """
    Reads rows from the given csv file and maps troops
    to the armour types they have.
    """
    weapon_input_path = create_and_check_path(weapon_input_filename, True)
    
    armour_types_dict = {}

    with open(weapon_input_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
    
        for row in csv_reader:
            if row[0] in armour_types:
                troops_with_armour_type = format_troops(row[1].split(","))
                armour_types_dict[row[0]] = troops_with_armour_type
    
    return generate_armour_type_dicts(armour_types_dict)


def format_troops(troops_raw: list):
    """
    Formats a list of troops from make the name
    like it's corresponding .lua file.
    """
    troops = set()
    for troop in troops_raw:
        troop = troop.strip()
        troop = troop.replace(" ", "_")
        troop += ".lua"

        if troop != ".lua": troops.add(troop)
    
    return troops


def generate_armour_type_dicts(armour_types_dict: dict):
    """
    From the armour type > troop mapped dictionary, creates
    a troop > armour type dictionary.
    """
    troops_to_armour_types_dict = {}

    for armour_type, troops in armour_types_dict.items():
        for troop in troops:
            if troop not in troops_to_armour_types_dict:
                troops_to_armour_types_dict[troop] = armour_type


    joint_dict = {"armourTypeToTroops": armour_types_dict, "troopsToArmourType": troops_to_armour_types_dict}
    return joint_dict