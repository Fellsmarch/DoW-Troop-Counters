import logging

from weapons import collate_weapon_data
from troops import collate_troop_data
from armour_types import map_troops_to_armour_types
from file_handlers import create_and_check_path, load_from_json, save_to_json


class DamageInfo():
    def __init__(self, troop_file, weapon, damage):
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


def calculate_counters(armour_types, weapons_dict, troops_dict):
    """
    Ranks each troop in each race damage against each armour type
    """
    final = {}

    for race in troops_dict:
        print(f"STARTING ON {race}")
        final[race] = create_dict_from_list(armour_types)

        for troop in troops_dict[race]:
            for weapon in troops_dict[race][troop]["weapons"]:
                for armour_type in armour_types:
                    new_damage_info = DamageInfo(troop, weapon, weapons_dict[weapon][armour_type])
                    final[race][armour_type].append(new_damage_info)
        
        print(f"FINISHED {race}")
        print(f"STARTING SORTING FOR {race}")
        for armour_type in final[race]:
            final[race][armour_type].sort(reverse=True)
        print(f"FINISHED SORTING FOR {race}\n")

    return final
            

def create_dict_from_list(input_list):
    """
    Creates a dictionary from an input list where the keys
    are the list items and the values are empty lists.
    """
    new_dict = {}
    for item in input_list:
        new_dict[item] = []

    return new_dict


def optimise_armour_types(armour_types_dict):
    """
    Removes any un-used armour types from the armour_types_dict.
    """
    optimised_armour_types = []
    armour_types = armour_types_dict["armourTypeToTroops"]
    for armour_type in armour_types:
        if armour_types[armour_type]:
            optimised_armour_types.append(armour_type)

    return optimised_armour_types


def main():
    config_filename = "config.json"
    config = load_from_json(config_filename)

    logging.info("test")

    armour_types_set, weapons_dict = collate_weapon_data(config["corsix_weapon_dps"])
    save_to_json(config["data"]["weapons"], weapons_dict)

    armour_types_dict = map_troops_to_armour_types(config["corsix_weapon_dps"], armour_types_set)
    save_to_json(config["data"]["armourTypes"], armour_types_dict)

    troops_dict = collate_troop_data(config["troops"], weapons_dict, armour_types_dict["troopsToArmourType"])
    save_to_json(config["data"]["troops"], troops_dict)

    optimised_armour_types = optimise_armour_types(armour_types_dict)
    save_to_json(config["data"]["optimisedArmourTypes"], optimised_armour_types)

    counters = calculate_counters(optimised_armour_types, weapons_dict, troops_dict)
    save_to_json(config["data"]["counters"], counters)


def run():
    """
    Alternate function for running the program
    """
    FORMAT = "%(asctime)s GENERATE DATA: %(message)s"
    logging.basicConfig(filename="logs.log", level=logging.INFO, format=FORMAT)

    main()


if __name__ == "__main__":
    main()