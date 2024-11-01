import tkinter as tk
from tkinter import filedialog
from config_manager import ConfigManager
from bot import PokemonBot
from concede import PokemonConcedeBot
from adb_utils import connect_to_emulator, take_screenshot

class BotUI:
    def __init__(self, root, app_state):
        self.root = root
        self.app_state = app_state
        self.root.title("Pokemon Pocket Bot")
        self.config_manager = ConfigManager()
        self.bot = PokemonBot(app_state, self.log_message)
        self.concede = PokemonConcedeBot(app_state, self.log_message)
        
        # Flags to track bot states
        self.auto_concede_active = False
        self.bot_running = False

        # UI setup
        self.setup_ui()
        self.load_configs()

    def setup_ui(self):
        self.root.geometry("400x550")  # Adjusted window height
        tk.Label(self.root, text="Pokemon Pocket Bot ⚔️", font=("Helvetica", 16, "bold")).pack(pady=10)

        # Frame to hold emulator path selection button and label
        select_path_frame = tk.Frame(self.root)
        select_path_frame.pack(pady=5)

        self.select_path_button = tk.Button(select_path_frame, text="Select Emulator Path", command=self.select_emulator_path, font=("Helvetica", 10))
        self.select_path_button.pack(side=tk.LEFT, padx=5)

        self.selected_emulator_label = tk.Label(select_path_frame, text="", font=("Helvetica", 10))
        self.selected_emulator_label.pack(side=tk.LEFT)

        # Frame for Start/Stop Bot button
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        # Start/Stop Bot button
        self.start_stop_button = tk.Button(button_frame, text="Start Bot", command=self.toggle_bot, width=12, relief=tk.RAISED, bd=3, font=("Helvetica", 10))
        self.start_stop_button.pack(side=tk.LEFT, padx=5)

        # Frame for Screenshot and Auto Concede buttons
        action_frame = tk.Frame(self.root)
        action_frame.pack(pady=10)

        # Auto Concede button
        self.auto_concede_button = tk.Button(action_frame, text="Auto Concede", command=self.toggle_auto_concede, width=12, relief=tk.RAISED, bd=3, font=("Helvetica", 10))
        self.auto_concede_button.pack(side=tk.LEFT, padx=5)

        # Screenshot button
        self.screenshot_button = tk.Button(action_frame, text="Screenshot", command=self.take_screenshot, width=12, relief=tk.RAISED, bd=3, font=("Helvetica", 10))
        self.screenshot_button.pack(side=tk.LEFT, padx=5)

        # Status and log sections
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

    def toggle_bot(self):
        """Toggle between starting and stopping the bot."""
        if not self.bot_running:
            # Start the bot
            self.bot_running = True
            self.start_stop_button.config(text="Stop Bot")
            self.status_label.config(text="Status: Running")
            self.log_message("Bot started.")
            
            # Run the bot in a separate thread to avoid blocking the UI
            self.bot.start()
        else:
            # Stop the bot
            self.bot.stop()  # Ensure this is called to cleanly stop any running process
            self.bot_running = False
            self.start_stop_button.config(text="Start Bot")
            self.status_label.config(text="Status: Not running")
            self.log_message("Bot stopped.")

    def toggle_auto_concede(self):
        """Toggle between starting and stopping the auto-concede functionality."""
        if not self.auto_concede_active:
            # Start Auto Concede
            self.auto_concede_active = True
            self.auto_concede_button.config(text="STOP Auto Concede")
            self.log_message("Auto Concede activated.")
            self.concede.start()  # Start the auto-concede logic in PokemonConcedeBot
        else:
            # Stop Auto Concede
            self.auto_concede_active = False
            self.auto_concede_button.config(text="Auto Concede")
            self.log_message("Auto Concede deactivated.")
            self.concede.stop()  # Stop the auto-concede logic in PokemonConcedeBot

    def select_emulator_path(self):
        emulator_path = filedialog.askdirectory()
        if emulator_path:
            self.config_manager.save("path", emulator_path)
            self.app_state.program_path = emulator_path
            self.selected_emulator_label.config(text=emulator_path)
            self.log_message("Emulator path selected and saved.")

    def take_screenshot(self):
        screenshot = take_screenshot()
        self.log_message("Screenshot taken.")
