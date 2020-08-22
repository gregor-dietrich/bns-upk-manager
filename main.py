import json
from datetime import datetime
from os import listdir, path, remove
from shutil import copyfile
from winreg import ConnectRegistry, EnumValue, HKEY_CURRENT_USER, HKEY_LOCAL_MACHINE, OpenKey

from init import charset, default_values, init, settings_location
from update import update
from tkutil import checksum


def find_game_path():
    # Try default install dir
    default = default_values["game_location"]
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


def restore_all():
    upk_list = listdir(settings["backup_location"])
    if len(upk_list) == 0:
        print("No files to restore!")
    else:
        move_files(upk_list, settings["backup_location"], settings["game_location"])


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
