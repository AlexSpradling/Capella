import tkinter as tk
import os
import ttkbootstrap as ttk


class SplashPage(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)

        self.create_splash_page()

    import os

    def create_splash_page(self):
        # Get the directory where splash_page.py is located
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Go one level up to the new_capella directory
        base_dir = os.path.dirname(current_dir)

        # Build the absolute path to splash_text.txt
        splash_text_path = os.path.join(base_dir, "text_files", "splash_text.txt")

        # Read splash_text.txt with utf-8 encoding
        with open(splash_text_path, "r", encoding="utf-8") as f:
            self.splash_text = f.read()

        # make font courier 12
        large_font = ("Courier New", 12)

        logo = """
                     ______                 ____
                    / ____/___ _____  ___  / / /___ _
                   / /   / __ `/ __ \/ _ \/ / / __ `/
                  / /___/ /_/ / /_/ /  __/ / / /_/ /
 _________________\____/\__,_/ .___/\___/_/_/\__,_/_________________
/_____/_____/_____/         /_/                  /_____/_____/_____/

        """

        # make logo label
        self.logo_label = ttk.Label(
            self, text=logo, font=large_font, anchor="center", justify="left"
        )

        # make label
        self.text_label = ttk.Label(
            self,
            text=self.splash_text,
            font=large_font,
            anchor="center",
            justify="center",
        )

        # make it red
        self.logo_label.config(foreground="red")

        # make button
        self.button = ttk.Button(
            self,
            text="I ACCEPT THE ABOVE TERMS",
            command=self.enter,
            style="primary.Outline.TButton",
        )

        # grid everything
        self.logo_label.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.text_label.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.button.pack(side=tk.TOP, fill=tk.BOTH, padx=10, pady=10, expand=True)

    def enter(self):
        self.destroy()
