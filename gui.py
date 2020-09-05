from tkinter import ttk, END

from ttkthemes import ThemedTk

from init import *


class UPKManager(ThemedTk):
    def __init__(self, move_upks, restore_all, *args, **kwargs):
        ThemedTk.__init__(self, *args, **kwargs)
        self.settings = init(silent=True)
        self.move_upks = move_upks
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


class MainFrame(ttk.Frame):
    def __init__(self, p, c):
        ttk.Frame.__init__(self, p)
        self.grid(row=0, column=0, sticky="w", padx=10, pady=10)
        # Setup labels & checkboxes for player classes
        label_count = 0
        for player_class in default_values["remove_animations"]:
            if player_class == "Archer":
                player_class = "Zen " + player_class
            row_ref = label_count // 2
            col_ref = 0
            if label_count % 2 != 0:
                col_ref = 3
            new_label = ttk.Label(self, text=player_class, font=c.font_style)
            if player_class == "Zen Archer":
                # player_class = "Archer"
                pass
            box_ani = ttk.Checkbutton(self, text="Animations")
            box_eff = ttk.Checkbutton(self, text="Effects")
            new_label.grid(row=row_ref, column=col_ref, sticky="w")
            box_ani.grid(row=row_ref, column=col_ref + 1, sticky="w")
            box_eff.grid(row=row_ref, column=col_ref + 2, sticky="w")
            # Increment label_count
            label_count -= -1
        # Setup label & checkbox for misc. effects
        new_label_other = ttk.Label(self, text="Other", font=c.font_style)
        new_label_other.grid(row=6, column=0, sticky="w")
        box_eff_other = ttk.Checkbutton(self, text="Effects")
        box_eff_other.grid(row=6, column=1, sticky="w")
        # box_eff_other.state(["selected"])
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
                                 command=lambda: c.show_frame(MainFrame))
        load_button.grid(row=7, column=4, sticky="w", pady=5)
        save_button = ttk.Button(self, text="Save...",
                                 command=lambda: c.show_frame(MainFrame))
        save_button.grid(row=7, column=5, sticky="w", pady=5)


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
        self.log_options_label = ttk.Label(self, text="Log Options", font=c.font_style)
        self.log_options_label.grid(row=2, column=0, sticky="w")
        self.log_save_box = ttk.Checkbutton(self, text="Save Log", variable=c.settings["log_save"])
        self.log_save_box.grid(row=2, column=1, sticky="w", padx=6)
        self.log_show_box = ttk.Checkbutton(self, text="Show Log", variable=c.settings["log_show"])
        self.log_show_box.grid(row=3, column=1, sticky="w", padx=6)
        self.gui_options_label = ttk.Label(self, text="GUI Options", font=c.font_style)
        self.gui_options_label.grid(row=4, column=0, sticky="w")
        self.gui_mode_box = ttk.Checkbutton(self, text="Enable GUI", variable=c.settings["gui_mode"])
        self.gui_mode_box.grid(row=4, column=1, sticky="w", padx=6)
        self.dark_mode_box = ttk.Checkbutton(self, text="Dark Mode", variable=c.settings["dark_mode"])
        self.dark_mode_box.grid(row=5, column=1, sticky="w", padx=6)
        # Setup buttons
        self.default_button = ttk.Button(self, text="Default",
                                         command=self.set_default)
        self.default_button.grid(row=0, column=2, sticky="w", padx=10, pady=5)
        self.detect_game_button = ttk.Button(self, text="Detect",
                                             command=lambda: self.detect_game(c))
        self.detect_game_button.grid(row=1, column=2, sticky="w", padx=10, pady=5)
        self.back_button = ttk.Button(self, text="Back",
                                      command=lambda: c.show_frame(MainFrame))
        self.back_button.grid(row=6, column=1, sticky="w", padx=9, pady=5)

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