from tkinter import ttk
from ttkthemes import ThemedTk
from os import path
from sys import exit

from init import default_values, version


class UPKManager(ThemedTk):
    def __init__(self, *args, **kwargs):
        ThemedTk.__init__(self, *args, **kwargs)
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

    def show_frame(self, c):
        this = self.frames[c]
        this.tkraise()


class MainFrame(ttk.Frame):
    def __init__(self, p, c):
        ttk.Frame.__init__(self, p)
        self.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        # Setup labels & checkboxes for player classes
        label_count = 0
        for player_class in default_values["remove_animations"]:
            row_ref = label_count // 2
            col_ref = 0
            if label_count % 2 != 0:
                col_ref = 3
            new_label = ttk.Label(self, text=player_class, font=c.font_style)
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
        box_eff_other.state(["selected"])
        # Setup Buttons
        apply_button = ttk.Button(self, text="Apply",
                                  command=lambda: c.show_frame(MainFrame))
        apply_button.grid(row=7, column=0, sticky="w")
        restore_button = ttk.Button(self, text="Restore",
                                    command=lambda: c.show_frame(MainFrame))
        restore_button.grid(row=7, column=1, sticky="w")
        settings_button = ttk.Button(self, text="Settings",
                                     command=lambda: c.show_frame(SettingsFrame))
        settings_button.grid(row=7, column=2, sticky="w")
        load_button = ttk.Button(self, text="Load...",
                                 command=lambda: c.show_frame(MainFrame))
        load_button.grid(row=7, column=4, sticky="w")
        save_button = ttk.Button(self, text="Save...",
                                 command=lambda: c.show_frame(MainFrame))
        save_button.grid(row=7, column=5, sticky="w")


class SettingsFrame(ttk.Frame):
    def __init__(self, p, c):
        ttk.Frame.__init__(self, p)
        self.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        # Setup Buttons
        back_button = ttk.Button(self, text="Back",
                                 command=lambda: c.show_frame(MainFrame))
        back_button.grid(row=0, column=0, sticky="w")
