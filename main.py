import json
from datetime import datetime
from hashlib import sha1
from os import listdir, mkdir, path, remove
from shutil import copyfile
from tkinter import messagebox

from gui import UPKManager
from init import charset, init
from update import update


def checksum(file_name):
    hash_obj = sha1()
    with open(file_name, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()


def log(string):
    if settings["log_save"] or settings["log_show"]:
        # Generate Timestamp
        timestamp = "(" + datetime.now().strftime("%H:%M:%S") + ") "
    else:
        return
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
                    print("ERROR: Checksum is invalid!")
                    errors_checksum += 1
                    if path.exists(dst + file_name):
                        remove(dst + file_name)
            else:
                print("ERROR: File not found! Skipping...")
                errors_path += 1
        except PermissionError:
            print("ERROR: Permission denied! Skipping...")
            errors_permission += 1
    if errors_checksum > 0:
        log("File checksum errors: " + str(errors_checksum) + "\n" + "Check your hard drive for errors!")
    if errors_permission > 0:
        log("Permission denied errors: " + str(errors_path) + "\n" + "Try running as admin!")
    if errors_path > 0:
        log("File not found errors: " + str(errors_path))


def move_upks(mode, category):
    if mode == "remove":
        src, dst = settings["game_location"], settings["backup_location"]
    elif mode == "restore":
        src, dst = settings["backup_location"], settings["game_location"]
    else:
        if settings["gui_mode"]:
            messagebox.showwarning("Error", "move_upks() can't be called without defining a mode!")
        else:
            print("Error: move_upks() can't be called without defining a mode!")
        return
    if category == "all":
        move_upks(mode, "animations")
        move_upks(mode, "effects")
        if settings["gui_mode"]:
            messagebox.showinfo("Removal Success", "All file operations finished.")
        else:
            print("... all file operations finished!")
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


def restore_all(silent=False):
    upk_list = listdir(settings["backup_location"])
    if len(upk_list) == 0:
        if settings["gui_mode"]:
            if not silent:
                messagebox.showwarning("Warning", "No files to restore!")
        else:
            if not silent:
                print("No files to restore!")
    else:
        move_files(upk_list, settings["backup_location"], settings["game_location"])
        if settings["gui_mode"]:
            if not silent:
                messagebox.showinfo("Restore Success", "All file operations finished.")
        else:
            print("... all file operations finished!")


# Check for Updates
update()
# Initialize Settings
settings = init()

# Do something!
if settings["dark_mode"]:
    theme = "equilux"
else:
    theme = "arc"
app = UPKManager(move_files, restore_all, theme=theme)
app.mainloop()
