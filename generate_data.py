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

    logging.debug("Loading weapon data")
    weapons_dict = load_from_json(config["data"]["weapons"])
    logging.debug("Done")

    logging.debug("Loading troop data")
    troops_dict = load_from_json(config["data"]["troops"])
    logging.debug("Done")

    for race in troops_dict:
        logging.info(f"Starting on {race}")

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

        logging.info(f"Finished {race}")

    logging.debug("Saving counters to file")
    save_to_json(config["data"]["counters"], counters)
    logging.debug("Done")


def sort_counters(counters: dict):
    """
    Sorts the counters into descending order.

    :param counters: the counters to sort

    :returns: the counters dict with sorted armour type counters
    """
    for race in counters:
        logging.info(f"Starting sorting for {race}")

        for armour_type in counters[race]:
            counters[race][armour_type].sort(reverse=True)

        logging.info(f"Finished sorting for {race}")

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
        logging.debug("Trying to load optimised armour types")
        armour_types = load_from_json(config["data"]["optimisedArmourTypes"])
    except PathNotFoundError:
        logging.warning(
            "Could not load optimised armour types, attempting to load non-optimised armour types")
        armour_types = load_from_json(config["data"]["armourTypes"])

    logging.debug("Successfully retrieved armour types")
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
    logging.debug("Loading armour types from file for optimisation")
    armour_types_dict = load_from_json(config["data"]["armourTypes"])
    logging.debug("Done")

    optimised_armour_types = []
    armour_types = armour_types_dict["armourTypeToTroops"]

    for armour_type in armour_types:
        if armour_types[armour_type]:
            optimised_armour_types.append(armour_type)

    logging.debug("Saving optimised armour types to file")
    save_to_json(config["data"]["optimisedArmourTypes"],
                 optimised_armour_types)
    logging.debug("Done")


def setup_logging(config: dict):
    """
    Sets up the logging configuration

    :param config: the configuration for the program
    """
    logging_level = config["loggingLevel"]
    FORMAT = "%(asctime)s GENERATE DATA: %(message)s"
    logging.basicConfig(filename="logs.log",
                        level=logging_level, format=FORMAT)


def generate_weapon_info_and_armour_types(config: dict):
    """
    Pulls the armour types and all weapons from the weapon config file,
    formats them and then saves the them to storage files.

    :param config: the configuration for the program
    """
    logging.debug("Collating armour types and weapon data")
    armour_types_set, weapons_dict = collate_weapon_data(
        config["corsix_weapon_dps"])
    logging.debug("Done")

    logging.debug("Saving weapons to file")
    save_to_json(config["data"]["weapons"], weapons_dict)
    logging.debug("Done")

    generate_armour_type_info(config, armour_types_set)


def generate_armour_type_info(config: dict, armour_types_set: set):
    """
    Generates the armour type dict containing the armour type to troops
    mapping and the troops to armour type mapping.

    :param config: the configuration for the program
    :param armour_types_set: the set of armour types
    """
    armour_type_file = config["corsix_weapon_dps"]

    logging.debug("Mapping troops to armour types")
    armour_types_dict = map_troops_to_armour_types(
        armour_type_file, armour_types_set)

    logging.debug("Saving armour types to file")
    save_to_json(config["data"]["armourTypes"], armour_types_dict)
    logging.debug("Done")


def generate_troop_info(config: dict):
    """
    Generates the troop information and saves it to a data file.

    :param config: the configuration for the program
    """
    logging.debug("Loading data files for weapons")
    weapons_dict = load_from_json(config["data"]["weapons"])
    logging.debug("Done")

    logging.debug("Loading data files for armour types")
    armour_types_dict = load_from_json(config["data"]["armourTypes"])
    logging.debug("Done")

    logging.debug("Collating troop data")
    troops_dict = collate_troop_data(
        config["troops"], weapons_dict, armour_types_dict["troopsToArmourType"])

    logging.debug("Saving troop data to file")
    save_to_json(config["data"]["troops"], troops_dict)
    logging.debug("Done")


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