import json
from os import mkdir, path, remove
from sys import exit
from winreg import ConnectRegistry, EnumValue, HKEY_CURRENT_USER, HKEY_LOCAL_MACHINE, OpenKey

charset = "utf-8"
settings_location = "./settings.json"
version = "0.5.1"

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


def find_game_path():
    default = default_values["game_location"]
    # Try default install dir
    if path.exists(default):
        return default
    # Search HKCU
    result = search_reg("HKCU")
    # Search HKLM
    if result is None:
        result = search_reg("HKLM")
    # Fix Backslashes
    try:
        if "\\" in result:
            result = result.split("\\")
            result = "/".join(result)
        if path.exists(result):
            return result
    except TypeError:
        pass


def search_reg(scope):
    if scope == "HKCU":
        a_reg = ConnectRegistry(None, HKEY_CURRENT_USER)
        a_key = "Software\\Classes\\Local Settings\\Software\\Microsoft\\Windows\\Shell\\MuiCache\\"
    elif scope == "HKLM":
        a_reg = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
        a_key = "SOFTWARE\\WOW6432Node\\NCWest\\BnS\\"
    else:
        return
    count = 0
    try:
        key = OpenKey(a_reg, a_key)
        while True:
            name, value, value_type = EnumValue(key, count)
            if scope == "HKCU":
                if value == "Blade & Soul by bloodlust(x86)":
                    game_path = name.split(".")[0].split("\\")
                    game_path.pop()
                    game_path.pop()
                    print("Game path found in HKCU!")
                    return "/".join(game_path) + "/"
            elif scope == "HKLM":
                if name == "BaseDir":
                    print("Game path found in HKLM!")
                    return value
            count += 1
    except (WindowsError, OSError, FileNotFoundError):
        pass


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
        game_path = find_game_path()
        if game_path is not None and path.exists(game_path):
            print("Success! Saving path to settings.json...")
            default_values["game_location"] = game_path
        else:
            print("Couldn't find game location. Please adjust manually in settings.json!")
        with open(settings_location, "w", encoding=charset) as settings_file:
            json.dump(default_values, settings_file, sort_keys=True, indent=4)
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
        # Create backup & profiles folders if needed
        for folder in [settings_values["backup_location"], "./profiles/"]:
            if not path.exists(folder):
                mkdir(folder)
        # Dumping settings_values to settings.json
        with open(settings_location, "w", encoding=charset) as settings_file:
            json.dump(settings_values, settings_file, sort_keys=True, indent=4)
        settings_values["game_location"] += "contents/bns/CookedPC/"
        print("Successfully initialized. Welcome, Cricket!")
        return settings_values
    except (json.JSONDecodeError, TypeError, AttributeError):
        print("ERROR: Invalid JSON syntax detected!")
        if input("Delete settings.json and generate default (y/n)? ") == "y":
            remove(settings_location)
            return init()
        else:
            print("Exiting...")
            exit()
