"""
Generates a list of how much damage each DoW troop does against each
armour type.

It does this by generating data files for: 
 - Weapons -- Each weapon and it's damage against each armour type
 - Armour types -- A list of armour types that exist in DoW
 - Optimised armour types -- A list off armour types that are used in DoW
 - Troops -- Every troop in DoW and which weapons they have. Organised by race

Harrison Cook
May 2020
"""

import logging

from weapons import collate_weapon_data
from troops import collate_troop_data
from armour_types import map_troops_to_armour_types
from file_handlers import create_and_check_path, load_from_json, save_to_json, PathNotFoundError


class DamageInfo():
    """
    A class to store information about a troop's damage.
    It has comparison functions so that we can .sort()
    a list of DamageInfo objects.
    """

    def __init__(self, troop_file: str, weapon: str, damage: float):
        """
        :param troop_file: the troop's .lua filename
        :param weapon: the associated weapon filename with this damage
        :param damage: the damage (per second) this weapon does to the
                        selected armour type
        """
        self.troop_file = troop_file
        self.weapon = weapon
        self.damage = damage

    def __eq__(self, other):
        return self.damage == other.damage

    def __ne__(self, other):
        return not (self.damage == other.damage)

    def __lt__(self, other):
        return self.damage < other.damage

    def __le__(self, other):
        return self.damage <= other.damage

    def __gt__(self, other):
        return self.damage > other.damage

    def __ge__(self, other):
        return self.damage >= other.damage


# I need to reduce the size of this function, it's a bit bloated
def calculate_counters(config: dict):
    """
    Ranks each troop in each race damage against each armour type.

    :param config: the configuration for the program
    :returns: a dictionary containing each race's troop damage against
                each armour type
    """
    counters = {}
    armour_types = get_armour_types(config)
    weapons_dict = load_from_json(config["data"]["weapons"])
    troops_dict = load_from_json(config["data"]["troops"])

    for race in troops_dict:
        logging.info(f"Starting finding counters for {race}")

        counters[race] = create_dict_from_list(armour_types)

        for troop in troops_dict[race]:  # For each troop in a race
            # For each weapon that troop has
            for weapon in troops_dict[race][troop]["weapons"]:
                for armour_type in armour_types:

                    new_damage_info = DamageInfo(
                        troop,
                        weapon,
                        weapons_dict[weapon][armour_type]
                    )

                    counters[race][armour_type].append(new_damage_info)

        logging.info(f"Finished finding counters for {race}")

    save_to_json(config["data"]["counters"], counters)


def sort_counters(counters: dict):
    """
    Sorts the counters into descending order.

    :param counters: the counters to sort
    :returns: the counters dict with sorted armour type counters
    """
    for race in counters:
        logging.info(f"Starting counters sorting for {race}")

        for armour_type in counters[race]:
            counters[race][armour_type].sort(reverse=True)

        logging.info(f"Finished counters sorting for {race}")

    return counters


def get_armour_types(config: dict):
    """
    Gets the armour types from file. Prioritises the optimised armour
    types

    :param config: the configuration for the program
    :returns: the armour types that were found
    """
    armour_types = None

    try:
        armour_types = load_from_json(config["data"]["optimisedArmourTypes"])
    except PathNotFoundError:
        logging.warning(
            "Could not load optimised armour types, attempting to load non-optimised armour types")
        armour_types = load_from_json(config["data"]["armourTypes"])

    return armour_types


def create_dict_from_list(input_list: list):
    """
    Creates a dictionary from an input list where the keys
    are the list items and the values are empty lists.

    :param input_list: a list of value to turn into a dictionary
    :returns: a dictionary with list items mapped to empty lists
    """
    new_dict = {}
    for item in input_list:
        new_dict[item] = []

    return new_dict


def optimise_armour_types(config: dict):
    """
    Removes any un-used armour types from the armour types and 
    saves the result to file.

    :param config: the configuration for the program
    """
    armour_types_dict = load_from_json(config["data"]["armourTypes"])

    optimised_armour_types = []
    armour_types = armour_types_dict["armourTypeToTroops"]

    for armour_type in armour_types:
        if armour_types[armour_type]:
            optimised_armour_types.append(armour_type)

    save_to_json(config["data"]["optimisedArmourTypes"],
                 optimised_armour_types)


def generate_weapon_info_and_armour_types(config: dict):
    """
    Pulls the armour types and all weapons from the weapon config file,
    formats them and then saves the them to storage files.

    :param config: the configuration for the program
    """
    logging.info("Collating armour types and weapon data")
    armour_types_set, weapons_dict = collate_weapon_data(
        config["corsix_weapon_dps"])
    logging.debug("Done")

    save_to_json(config["data"]["weapons"], weapons_dict)

    generate_armour_type_info(config, armour_types_set)


def generate_armour_type_info(config: dict, armour_types_set: set):
    """
    Generates the armour type dict containing the armour type to troops
    mapping and the troops to armour type mapping.

    :param config: the configuration for the program
    :param armour_types_set: the set of armour types
    """
    armour_type_file = config["corsix_weapon_dps"]

    logging.info("Mapping troops to armour types")
    armour_types_dict = map_troops_to_armour_types(
        armour_type_file, armour_types_set)

    save_to_json(config["data"]["armourTypes"], armour_types_dict)


def generate_troop_info(config: dict):
    """
    Generates the troop information and saves it to a data file.

    :param config: the configuration for the program
    """
    weapons_dict = load_from_json(config["data"]["weapons"])
    armour_types_dict = load_from_json(config["data"]["armourTypes"])

    logging.info("Collating troop data")
    troops_dict = collate_troop_data(
        config["troops"], weapons_dict, armour_types_dict["troopsToArmourType"])

    save_to_json(config["data"]["troops"], troops_dict)


def setup_logging(config: dict):
    """
    Sets up the logging configuration

    :param config: the configuration for the program
    """
    logging_level = config["loggingLevel"]
    filemode = "w" if config["loggingOverwrite"] else "a"
    FORMAT = "%(asctime)s %(levelname)s: %(message)s"
    logging.basicConfig(filename="generate_data.log",
                        level=logging_level, format=FORMAT, filemode=filemode)


def run():
    config_filename = "config.json"
    config = load_from_json(config_filename)

    setup_logging(config)

    logging.info("Starting generation of data")

    generate_weapon_info_and_armour_types(config)

    generate_troop_info(config)

    optimise_armour_types(config)

    calculate_counters(config)

    logging.info("Finished generating data\n\n")


if __name__ == "__main__":
    run()
