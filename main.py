import json
from datetime import datetime
from hashlib import sha1
from os import listdir, mkdir, path, remove
from shutil import copyfile
from sys import exit
from tkinter import messagebox

from env import *
from gui import find_game_path, UPKManager


def checksum(file_name):
    hash_obj = sha1()
    with open(file_name, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()


def init(silent=False):
    # Check if required data is present
    if not path.exists("./data/animations.json") or not path.exists("./data/effects.json"):
        if not silent:
            messagebox.showerror("CRITICAL ERROR", "Required data is missing! Exiting...")
            return
        try:
            exit()
        except SystemExit:
            pass
    # Generate default settings.json if there is none
    if not path.exists(settings_location):
        game_path = find_game_path()
        if game_path is not None and path.exists(game_path):
            default_values["game_location"] = game_path
        else:
            messagebox.showwarning("Warning", "Couldn't find game location.\nPlease adjust manually in settings!")
        with open(settings_location, "w", encoding=charset) as settings_file:
            json.dump(default_values, settings_file, sort_keys=True, indent=4)
    # Load settings.json as dictionary
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
        return settings_values
    except (json.JSONDecodeError, TypeError, AttributeError):
        if messagebox.askquestion("Error",
                                  "Invalid JSON syntax detected!\n" +
                                  "Delete settings.json and generate default? ") == "yes":
            remove(settings_location)
            return init()
        else:
            exit()


def log(string):
    # Generate Timestamp
    timestamp = "(" + datetime.now().strftime("%H:%M:%S") + ") "
    # Show Logs
    print(timestamp + string)
    # Save Logs
    if settings["log_save"]:
        logfile = "./log/" + datetime.now().strftime("%Y.%m.%d.txt")
        if not path.exists("./log/"):
            mkdir("./log/")
        with open(logfile, "a", encoding=charset) as file:
            file.write(timestamp + string + "\n")


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
    if errors_checksum > 0:
        log("File checksum errors: " + str(errors_checksum) + "\n" + "Check your hard drive for errors!")
    if errors_permission > 0:
        log("Permission denied errors: " + str(errors_path) + "\n" + "Try running as admin!")
    if errors_path > 0:
        log("File not found errors: " + str(errors_path))


def restore_all(silent=False):
    upk_list = listdir(settings["backup_location"])
    if len(upk_list) == 0:
        if not silent:
            messagebox.showwarning("Warning", "No files to restore!")
            log("No files to restore!")
    else:
        move_files(upk_list, settings["backup_location"], settings["game_location"])
        if not silent:
            messagebox.showinfo("Restore Success", "All file operations finished.")
            log("... all file operations finished!")


# Initialize Settings
settings = init()

# Do something!
if settings["dark_mode"]:
    theme = "equilux"
else:
    theme = "arc"
# Start App
app = UPKManager(move_files, restore_all, settings, theme=theme)
app.update()
app.mainloop()
