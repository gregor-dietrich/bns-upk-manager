import json
from datetime import datetime
from os import listdir, mkdir, path, remove
from shutil import copyfile
from tkinter import messagebox

from gui import UPKManager
from init import charset, default_values, find_game_path, init, settings_location
from tkutil import checksum, settings_load
from update import update


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
            messagebox.showinfo("Restore Success", "All file operations finished.")
        else:
            print("... all file operations finished!")


# Check for Updates
update()
# Initialize Settings
settings = init()
# Read profiles folder
profiles = listdir("./profiles/")
for profile in profiles:
    if not profile.endswith(".json"):
        profiles.remove(profile)

# Do something!
if settings["gui_mode"]:
    if settings["dark_mode"]:
        theme = "equilux"
    else:
        theme = "arc"
    app = UPKManager(move_upks, restore_all, theme=theme)
    app.mainloop()
else:
    while True:
        print("(0) Exit UPK Manager")
        print("(1) Apply current profile (settings.json)")
        print("(2) Restore EVERYTHING from backup folder")
        print("(3) Detect Blade & Soul folder")

        offset = 4
        for profile_number in range(len(profiles)):
            print("(%i) Load Profile '%s'" % ((profile_number + offset), profiles[profile_number]))

        try:
            command = int(input("What would you like to do: "))
            if command == 0:
                print("Goodbye, Cricket!")
                break
            elif command in range(offset):
                if command == 1:
                    restore_all(silent=True)
                    move_upks("remove", "all")
                elif command == 2:
                    restore_all()
                elif command == 3:
                    game_folder = find_game_path()
                    if game_folder is not None:
                        print("Success! Saving path to settings.json...")
                        settings["game_location"] = game_folder
                        with open(settings_location, "w", encoding=charset) as settings_file:
                            json.dump(settings, settings_file, sort_keys=True, indent=4)
                        settings["game_location"] += "contents/bns/CookedPC/"
                    else:
                        print("Couldn't detect game folder.")
            elif command in range(offset, (len(profiles) + offset)):
                settings = settings_load(("./profiles/" + profiles[(command - offset)]), default_values, charset)
                with open(settings_location, "w", encoding=charset) as settings_file:
                    json.dump(settings, settings_file, sort_keys=True, indent=4)
            else:
                raise ValueError
        except ValueError:
            print("Invalid input: Enter an integer between 0 and %i!" % (len(profiles) + (offset - 1)))
