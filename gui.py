import json
from os import path
from sys import exit
from tkinter import filedialog, messagebox, IntVar, ttk, END
from ttkthemes import ThemedTk
from winreg import ConnectRegistry, EnumValue, HKEY_CURRENT_USER, HKEY_LOCAL_MACHINE, OpenKey

from env import *
from update import update


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
                    # print("Game path found in HKCU!")
                    return "/".join(game_path) + "/"
            elif scope == "HKLM":
                if name == "BaseDir":
                    # print("Game path found in HKLM!")
                    return value
            count += 1
    except (WindowsError, OSError, FileNotFoundError):
        pass


class UPKManager(ThemedTk):
    def __init__(self, move_files, restore_all, settings, *args, **kwargs):
        ThemedTk.__init__(self, *args, **kwargs)
        self.settings = settings
        self.update = update
        self.move_files = move_files
        self.restore_all = restore_all
        # Setup Window
        self.title("UPK Manager for Blade & Soul v" + version)
        if self.current_theme == "equilux":
            self.bg_color = "#464646"
        elif self.current_theme == "yaru":
            self.bg_color = "#F5F5F5"
        else:
            self.bg_color = ""
        self.config(background=self.bg_color)
        self.font_style = "Candara 11 bold"
        self.geometry("+700+300")
        self.resizable(0, 0)
        if path.isfile("upk_manager.ico"):
            self.iconbitmap(bitmap="upk_manager.ico")
        # Setup Container
        container = ttk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        # Setup Frame dict
        self.frames = {}
        for item in (MainFrame, SettingsFrame):
            frame = item(container, self)
            self.frames[item] = frame
            frame.grid(row=0, column=0, sticky="nesw")
        # Show default frame
        self.show_frame(MainFrame)

    def __del__(self):
        try:
            exit()
        except SystemExit:
            pass

    def apply(self):
        self.restore_all(silent=True)
        self.move_upks("remove", "all")

    def show_frame(self, c):
        this = self.frames[c]
        this.tkraise()

    def move_upks(self, mode, category):
        if mode == "remove":
            src, dst = self.settings["game_location"], self.settings["backup_location"]
        elif mode == "restore":
            src, dst = self.settings["backup_location"], self.settings["game_location"]
        else:
            messagebox.showwarning("Error", "move_upks() can't be called without defining a mode!")
            return
        if category == "all":
            self.move_upks(mode, "animations")
            self.move_upks(mode, "effects")
            messagebox.showinfo("Removal Success", "All file operations finished.")
            print("... all file operations finished!")
        else:
            # Generate list of files from json
            upk_list = []
            with open("./data/" + category + ".json", "r", encoding=charset) as upks:
                values = upks.read()
            upk_values = json.loads(values)
            for player_class in upk_values.keys():
                if player_class not in self.settings["remove_" + category]:
                    continue
                for value in upk_values[player_class]:
                    upk_list.append(value)
            self.move_files(upk_list, src, dst)


class MainFrame(ttk.Frame):
    def __init__(self, p, c):
        ttk.Frame.__init__(self, p)
        self.grid(row=0, column=0, sticky="w", padx=10, pady=10)
        # Setup labels & checkboxes for player classes
        label_count = 0
        self.box_ani_vars = {}
        self.box_eff_vars = {}
        for player_class in default_values["remove_animations"]:
            if player_class == "Archer":
                player_class = "Zen " + player_class
            row_ref = label_count // 2
            col_ref = 0
            if label_count % 2 != 0:
                col_ref = 3
            new_label = ttk.Label(self, text=player_class, font=c.font_style)
            if player_class == "Zen Archer":
                player_class = "Archer"
            self.box_ani_vars[player_class] = IntVar()
            if player_class in c.settings["remove_animations"]:
                self.box_ani_vars[player_class].set(1)
            box_ani = ttk.Checkbutton(self, text="Animations", variable=self.box_ani_vars[player_class])
            self.box_eff_vars[player_class] = IntVar()
            if player_class in c.settings["remove_effects"]:
                self.box_eff_vars[player_class].set(1)
            box_eff = ttk.Checkbutton(self, text="Effects", variable=self.box_eff_vars[player_class])
            new_label.grid(row=row_ref, column=col_ref, sticky="w")
            box_ani.grid(row=row_ref, column=col_ref + 1, sticky="w")
            box_eff.grid(row=row_ref, column=col_ref + 2, sticky="w")
            # Increment label_count
            label_count -= -1
        # Setup label & checkbox for misc. effects
        new_label_other = ttk.Label(self, text="Other", font=c.font_style)
        new_label_other.grid(row=6, column=0, sticky="w")
        self.box_eff_vars["other"] = IntVar()
        if "other" in c.settings["remove_effects"]:
            self.box_eff_vars["other"].set(1)
        box_eff_other = ttk.Checkbutton(self, text="Effects", variable=self.box_eff_vars["other"])
        box_eff_other.grid(row=6, column=1, sticky="w")
        # Setup buttons
        apply_button = ttk.Button(self, text="Apply",
                                  command=c.apply)
        apply_button.grid(row=7, column=0, sticky="w", pady=5)
        restore_button = ttk.Button(self, text="Restore",
                                    command=c.restore_all)
        restore_button.grid(row=7, column=1, sticky="w", pady=5)
        settings_button = ttk.Button(self, text="Settings",
                                     command=lambda: c.show_frame(SettingsFrame))
        settings_button.grid(row=7, column=2, sticky="w", pady=5)
        load_button = ttk.Button(self, text="Load...",
                                 command=lambda: self.load_pro_file(c))
        load_button.grid(row=7, column=4, sticky="w", pady=5)
        save_button = ttk.Button(self, text="Save...",
                                 command=lambda: self.save_pro_file(c))
        save_button.grid(row=7, column=5, sticky="w", pady=5)

    def load_pro_file(self, c):
        try:
            file_name = filedialog.askopenfilename(initialdir="./profiles", title="Load Profile...",
                                                   filetypes=(("json files", "*.json"), ("all files", "*.*")))
            with open(file_name, "r", encoding=charset) as f:
                profile_values = f.read()
            profile_settings = json.loads(profile_values)
            c.settings["remove_animations"] = profile_settings["remove_animations"]
            c.settings["remove_effects"] = profile_settings["remove_effects"]
            for player_class in default_values["remove_animations"]:
                if player_class in c.settings["remove_animations"]:
                    self.box_ani_vars[player_class].set(1)
                else:
                    self.box_ani_vars[player_class].set(0)
            for player_class in default_values["remove_effects"]:
                if player_class in c.settings["remove_effects"]:
                    self.box_eff_vars[player_class].set(1)
                else:
                    self.box_eff_vars[player_class].set(0)
        except FileNotFoundError:
            pass

    def save_pro_file(self, c):
        file_name = filedialog.asksaveasfilename(initialdir="./profiles", title="Save Profile...",
                                                 filetypes=(("json files", "*.json"), ("all files", "*.*")))
        file_name = file_name.split(".")
        if file_name[-1] != "json":
            file_name.append("json")
        file_name = ".".join(file_name)
        profile_settings = {"remove_animations": c.settings["remove_animations"],
                            "remove_effects": c.settings["remove_effects"]}
        with open(file_name, "w", encoding=charset) as f:
            json.dump(profile_settings, f, sort_keys=True, indent=4)


class SettingsFrame(ttk.Frame):
    def __init__(self, p, c):
        ttk.Frame.__init__(self, p)
        self.grid(row=0, column=0, sticky="w", padx=10, pady=10)
        # Setup labels, inputs & checkboxes
        self.backup_location_label = ttk.Label(self, text="Backup Location", font=c.font_style)
        self.backup_location_label.grid(row=0, column=0, sticky="w")
        self.backup_location_input = ttk.Entry(self)
        self.backup_location_input.insert(0, c.settings["backup_location"])
        self.backup_location_input.grid(row=0, column=1, sticky="w", padx=10, pady=2, ipady=2)
        self.game_location_label = ttk.Label(self, text="Game Location", font=c.font_style)
        self.game_location_label.grid(row=1, column=0, sticky="w")
        self.game_location_input = ttk.Entry(self)
        self.game_location_input.insert(0, c.settings["game_location"][:-22])
        self.game_location_input.grid(row=1, column=1, sticky="w", padx=10, pady=2, ipady=2)
        self.log_save_var = IntVar()
        self.log_save_var.set(c.settings["log_save"])
        self.log_save_box = ttk.Checkbutton(self, text="Save Log", variable=self.log_save_var)
        self.log_save_box.grid(row=2, column=1, sticky="w", padx=6)
        self.dark_mode_var = IntVar()
        self.dark_mode_var.set(c.settings["dark_mode"])
        self.dark_mode_box = ttk.Checkbutton(self, text="Dark Mode", variable=self.dark_mode_var)
        self.dark_mode_box.grid(row=3, column=1, sticky="w", padx=6)
        # Setup buttons
        self.default_button = ttk.Button(self, text="Default",
                                         command=self.set_default)
        self.default_button.grid(row=0, column=2, sticky="w", padx=10, pady=5)
        self.detect_game_button = ttk.Button(self, text="Detect",
                                             command=lambda: self.detect_game(c))
        self.detect_game_button.grid(row=1, column=2, sticky="w", padx=10, pady=5)
        self.back_button = ttk.Button(self, text="Back",
                                      command=lambda: c.show_frame(MainFrame))
        self.back_button.grid(row=4, column=1, sticky="w", padx=9, pady=5)

    def detect_game(self, c):
        game_folder = find_game_path()
        if game_folder is not None:
            self.game_location_input.delete(0, END)
            self.game_location_input.insert(0, game_folder)
            c.settings["game_location"] = game_folder
            with open(settings_location, "w", encoding=charset) as settings_file:
                json.dump(c.settings, settings_file, sort_keys=True, indent=4)
            c.settings["game_location"] += "contents/bns/CookedPC/"
        else:
            messagebox.showerror("Error", "Couldn't detect game folder.")

    def set_default(self):
        self.backup_location_input.delete(0, END)
        self.backup_location_input.insert(0, default_values["backup_location"])
