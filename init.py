import json
from os import mkdir, path, remove
from sys import exit

from tkutil import find_game_path

charset = "utf-8"
settings_location = "./settings.json"
version = "0.4.7"

default_values = {
    "backup_location": "./backup/",
    "game_location": "C:/Program Files (x86)/NCSOFT/BnS/",
    "log_save": 0,
    "log_show": 1,
    "remove_animations":
        [
            "Blade Master",
            "Kung-Fu Master",
            "Force Master",
            "Destroyer",
            "Gunslinger",
            "Assassin",
            "Summoner",
            "Blade Dancer",
            "Warlock",
            "Soul Fighter",
            "Warden",
            "Archer"
        ],
    "remove_effects":
        [
            "Blade Master",
            "Kung-Fu Master",
            "Force Master",
            "Destroyer",
            "Gunslinger",
            "Assassin",
            "Summoner",
            "Blade Dancer",
            "Warlock",
            "Soul Fighter",
            "Warden",
            "Archer",
            "other"
        ]
}


def init():
    print("Initializing UPK Manager for Blade & Soul by Takku#0822 v" + version + "...")
    # Check if required data is present
    if not path.exists("./data/animations.json") or not path.exists("./data/effects.json"):
        input("CRITICAL ERROR: Required data is missing! Exiting...")
        exit()
    # Generate default settings.json if there is none
    if not path.exists(settings_location):
        print("File settings.json not found! Generating default...\n"
              + "Trying to detect game folder...")
        game_path = find_game_path(default_values["game_location"])
        if game_path is not None and path.exists(game_path):
            print("Success! Saving path to settings.json...")
            default_values["game_location"] = game_path
        else:
            print("Couldn't find game location. Please adjust manually in settings.json!")
        with open(settings_location, "w", encoding=charset) as file:
            json.dump(default_values, file, sort_keys=True, indent=4)
        print("Successfully generated. Please adjust your settings.json!")
        input("Save your changes to settings.json and press Enter to continue...")
    # Load settings.json as dictionary
    print("Loading settings from settings.json...")
    with open(settings_location, "r", encoding=charset) as file:
        values = file.read()
    try:
        settings_values = json.loads(values)
        for k in default_values.keys():
            if k not in settings_values.keys():
                settings_values[k] = default_values[k]
        settings_values["game_location"] += "contents/bns/CookedPC/"
        # Create backup folder if there is none
        if not path.exists(settings_values["backup_location"]):
            mkdir(settings_values["backup_location"])
        print("Successfully initialized. Welcome, Cricket!")
        return settings_values
    except json.JSONDecodeError:
        print("ERROR: Invalid JSON syntax detected!")
        if input("Delete settings.json and generate default (y/n)? ") == "y":
            remove(settings_location)
            return init()
        else:
            print("Exiting...")
            exit()
