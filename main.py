from bs4 import BeautifulSoup
from datetime import datetime
from hashlib import sha1
import json
from os import mkdir, listdir, path, remove, system
from requests import get
from shutil import copyfile
from sys import exit
from winreg import ConnectRegistry, EnumValue, HKEY_CURRENT_USER, HKEY_LOCAL_MACHINE, OpenKey

charset = "utf-8"
settings_location = "./settings.json"
version = "0.43"


def init():
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
    print("Initializing UPK Manager for Blade & Soul by Takku#0822 v" + version + "...")
    # Check if required data is present
    if not path.exists("./data/animations.json") or not path.exists("./data/effects.json"):
        input("CRITICAL ERROR: Required data is missing! Ragequitting...")
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


def checksum(file_name):
    hash_obj = sha1()
    with open(file_name, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()


def find_game_path():
    # Try default install dir
    default = "C:/Program Files (x86)/NCSOFT/BnS/"
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
    except TypeError:
        pass
    if path.exists(result):
        return result


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


def log(string):
    if settings["log_save"] or settings["log_show"]:
        # Generate Timestamp
        timestamp = "(" + datetime.now().strftime("%H:%M:%S") + ") "
    # Save Logs
    if settings["log_save"]:
        logfile = "./log/" + datetime.now().strftime("%Y.%m.%d.txt")
        if not path.exists("./log/"):
            mkdir("./log/")
        with open(logfile, "a", encoding=charset) as file:
            file.write(timestamp + string + "\n")
    # Show Logs
    if settings["log_show"]:
        print(timestamp + string)


def move_upks(mode, category):
    if mode == "remove":
        src, dst = settings["game_location"], settings["backup_location"]
    elif mode == "restore":
        src, dst = settings["backup_location"], settings["game_location"]
    else:
        print("ERROR: move_upks() can't be called without defining a mode!")
        return
    if category == "all":
        move_upks(mode, "animations")
        move_upks(mode, "effects")
    else:
        # Generate list of files from json
        upk_list = []
        with open("./data/" + category + ".json", "r", encoding=charset) as upks:
            values = upks.read()
        upk_values = json.loads(values)
        for player_class in upk_values.keys():
            if player_class not in settings["remove_" + category]:
                continue
            for value in upk_values[player_class]:
                upk_list.append(value)
        move_files(upk_list, src, dst)


def move_files(files, src, dst):
    errors_path = 0
    errors_checksum = 0
    errors_permission = 0
    # Take a list of files and removes them after moving them
    for file in files:
        file_name = file.strip()
        if not file_name.endswith(".upk"):
            file_name += ".upk"
        file_path = src + file_name
        log("Copying " + file_path + " to " + dst + file_name + "...")
        try:
            if path.exists(file_path):
                source_file = checksum(file_path)
                copyfile(file_path, dst + file_name)
                target_file = checksum(dst + file_name)
                log("Validating checksum...")
                if source_file == target_file:
                    log("Checksum is valid! Removing " + file_path + "...")
                    remove(file_path)
                else:
                    log("ERROR: Checksum is invalid!")
                    errors_checksum += 1
                    if path.exists(dst + file_name):
                        remove(dst + file_name)
            else:
                log("ERROR: File not found! Skipping...")
                errors_path += 1
        except PermissionError:
            log("ERROR: Permission denied! Skipping...")
            errors_permission += 1
    print("... all file operations finished!")
    if errors_checksum > 0:
        print("File checksum errors: " + str(errors_checksum) + "\n" + "Check your hard drive for errors!")
    if errors_permission > 0:
        print("Permission denied errors: " + str(errors_path) + "\n" + "Try running as admin!")
    if errors_path > 0:
        print("File not found errors: " + str(errors_path))


def restore_all():
    upk_list = listdir(settings["backup_location"])
    if len(upk_list) == 0:
        print("No files to restore!")
    else:
        move_files(upk_list, settings["backup_location"], settings["game_location"])


def update(repo="gregor-dietrich/bns-upk-manager", current_version=version):
    print("Checking for updates...")
    try:
        response = get("https://github.com/" + repo + "/releases/latest")
    except ConnectionError:
        print("Connection failed! Is your internet connection working?")
        return
    try:
        doc = BeautifulSoup(response.text, "html.parser")
        latest_version = doc.select_one("div.label-latest div ul li a")["title"].split("v")[1]
        file_url = "https://github.com" + doc.select_one("details div.Box div div.Box-body a")["href"]
        file_name = file_url.split("/")[-1]
        if float(latest_version) > float(current_version):
            decision = ""
            while decision not in ["y", "n"]:
                decision = input("New version found! Download now (y/n)? ")
                if decision == "y":
                    break
                elif decision == "n":
                    return
            if not path.exists("./" + file_name):
                file_binary = get(file_url)
                with open("./" + file_name, "wb") as file:
                    file.write(file_binary.content)
            if file_name.endswith(".zip"):
                from zipfile import ZipFile
            elif file_name.endswith(".7z"):
                from py7zr import SevenZipFile as ZipFile
            else:
                print("Invalid archive format!")
                return
            with ZipFile("./" + file_name, "r") as archive:
                archive.extractall("./download")
            with open("./update.bat", "w") as batch:
                batch.write("@echo off\n")
                patch_files = listdir("./download")
                for patch_file in patch_files:
                    if patch_file.endswith(".exe"):
                        batch.write("taskkill /f /im " + patch_file + "\n")
                batch.write("@ping -n 3 localhost> nul\n" +
                            "robocopy download\\ .\\ *.* /move /s /is /it\n" +
                            "rmdir /s /q download\n" +
                            "del " + file_name + "\n"
                            "del update.bat\n" +
                            "tk_upk_manager.exe")
            system('cmd /c "update.bat"')
            exit()
        else:
            print("Already up to date!")
    except (TypeError, ValueError, IndexError):
        print("Something went wrong! Please try again later.")


# Check for Updates
update()

# Initialize Settings
settings = init()

# Do something!
while True:
    print("(1) Apply current profile (settings.json)")
    print("(2) Restore EVERYTHING from backup folder")
    print("(3) Detect Blade & Soul folder")
    print("(0) Exit UPK Manager")

    try:
        command = int(input("What would you like to do: "))
        if command == 0:
            print("Goodbye, Cricket!")
            break
        elif command in range(4):
            if command == 1:
                restore_all()
                move_upks("remove", "all")
            elif command == 2:
                restore_all()
            elif command == 3:
                game_folder = find_game_path()
                if game_folder is None:
                    print("Couldn't detect game folder.")
                else:
                    print("Success! Saving path to settings.json...")
                    settings["game_location"] = game_folder
                    with open(settings_location, "w", encoding=charset) as settings_file:
                        json.dump(settings, settings_file, sort_keys=True, indent=4)
                    settings["game_location"] += "contents/bns/CookedPC/"
        else:
            raise ValueError
    except ValueError:
        print("Invalid input: Enter an integer between 0 and 3!")
