import tkinter as tk
from tkinter import filedialog
from config_manager import ConfigManager
from bot import PokemonBot
from adb_utils import connect_to_emulator

class BotUI:
    def __init__(self, root, app_state):
        self.root = root
        self.app_state = app_state
        self.root.title("Pokemon Pocket Bot")
        self.config_manager = ConfigManager()
        self.bot = PokemonBot(app_state, self.log_message)

        # UI setup
        self.setup_ui()
        self.load_configs()

    def setup_ui(self):
        self.root.geometry("400x500")  # Set initial window size
        tk.Label(self.root, text="Pokemon Pocket Bot ⚔️", font=("Helvetica", 16, "bold")).pack(pady=10)

        # Frame to hold emulator path selection button and label
        select_path_frame = tk.Frame(self.root)
        select_path_frame.pack(pady=5)

        self.select_path_button = tk.Button(select_path_frame, text="Select Emulator Path", command=self.select_emulator_path, font=("Helvetica", 10))
        self.select_path_button.pack(side=tk.LEFT, padx=5)

        self.selected_emulator_label = tk.Label(select_path_frame, text="", font=("Helvetica", 10))
        self.selected_emulator_label.pack(side=tk.LEFT)

        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        self.start_button = tk.Button(button_frame, text="Start Bot", command=self.start_bot, width=12, relief=tk.RAISED, bd=3, font=("Helvetica", 10))
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(self.root, text="Stop Script", command=self.stop_bot, state=tk.DISABLED, width=12, relief=tk.RAISED, bd=3, font=("Helvetica", 10))
        self.stop_button.pack(pady=10)

        self.status_label = tk.Label(self.root, text="Status: Not running", font=("Helvetica", 10))
        self.status_label.pack()

        self.log_text = tk.Text(self.root, font=("Helvetica", 10))
        self.log_text.pack()

    def load_configs(self):
        config = self.config_manager.load()
        if config:
            self.app_state.update(config)
            self.selected_emulator_label.config(text=self.app_state.program_path)

    def log_message(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

    def start_bot(self):
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text="Status: Running")
        self.bot.start()

    def stop_bot(self):
        self.bot.stop()
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Not running")

    def select_emulator_path(self):
        emulator_path = filedialog.askdirectory()
        if emulator_path:
            self.config_manager.save("path", emulator_path)
            self.app_state.program_path = emulator_path
            self.selected_emulator_label.config(text=emulator_path)
            self.log_message("Emulator path selected and saved.")

