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
        
        self.auto_concede_active = False
        self.bot_running = False

        self.setup_ui()
        self.load_configs()

    def setup_ui(self):
        self.root.geometry("400x650")
        tk.Label(self.root, text="Pokemon Pocket Bot ⚔️", font=("Helvetica", 16, "bold")).pack(pady=10)

        select_path_frame = tk.Frame(self.root)
        select_path_frame.pack(pady=5)

        self.select_path_button = tk.Button(select_path_frame, text="Select Emulator Path", command=self.select_emulator_path, font=("Helvetica", 10))
        self.select_path_button.pack(side=tk.LEFT, padx=5)

        self.selected_emulator_label = tk.Label(select_path_frame, text="", font=("Helvetica", 10))
        self.selected_emulator_label.pack(side=tk.LEFT)

        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        self.start_stop_button = tk.Button(button_frame, text="Start Bot", command=self.toggle_bot, width=20, relief=tk.RAISED, bd=3, font=("Helvetica", 10))
        self.start_stop_button.pack(side=tk.LEFT, padx=5)

        action_frame = tk.Frame(self.root)
        action_frame.pack(pady=10)

        self.auto_concede_button = tk.Button(action_frame, text="Auto Concede", command=self.toggle_auto_concede, width=20, relief=tk.RAISED, bd=3, font=("Helvetica", 10))
        self.auto_concede_button.pack(side=tk.LEFT, padx=5)

        self.screenshot_button = tk.Button(action_frame, text="Screenshot", command=self.take_screenshot, width=20, relief=tk.RAISED, bd=3, font=("Helvetica", 10))
        self.screenshot_button.pack(side=tk.LEFT, padx=5)

        region_frame = tk.Frame(self.root)
        region_frame.pack(pady=10)

        tk.Label(region_frame, text="Start X:", font=("Helvetica", 10)).grid(row=0, column=0, padx=5)
        self.start_x_entry = tk.Entry(region_frame, width=15, font=("Helvetica", 10))
        self.start_x_entry.grid(row=0, column=1)

        tk.Label(region_frame, text="Start Y:", font=("Helvetica", 10)).grid(row=0, column=2, padx=5)
        self.start_y_entry = tk.Entry(region_frame, width=15, font=("Helvetica", 10))
        self.start_y_entry.grid(row=0, column=3)

        tk.Label(region_frame, text="Width:", font=("Helvetica", 10)).grid(row=1, column=0, padx=5)
        self.width_entry = tk.Entry(region_frame, width=15, font=("Helvetica", 10))
        self.width_entry.grid(row=1, column=1)

        tk.Label(region_frame, text="Height:", font=("Helvetica", 10)).grid(row=1, column=2, padx=5)
        self.height_entry = tk.Entry(region_frame, width=15, font=("Helvetica", 10))
        self.height_entry.grid(row=1, column=3)

        self.region_screenshot_button = tk.Button(region_frame, text="Capture Region", command=self.take_region_screenshot, width=20, relief=tk.RAISED, bd=3, font=("Helvetica", 10))
        self.region_screenshot_button.grid(row=2, column=0, columnspan=4, pady=10)

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
        if not self.bot_running:
            self.bot_running = True
            self.start_stop_button.config(text="Stop Bot")
            self.status_label.config(text="Status: Running")
            self.log_message("Bot started.")
            
            self.bot.start()
        else:
            self.bot.stop()
            self.bot_running = False
            self.start_stop_button.config(text="Start Bot")
            self.status_label.config(text="Status: Not running")
            self.log_message("Bot stopped.")

    def toggle_auto_concede(self):
        if not self.auto_concede_active:
            self.auto_concede_active = True
            self.auto_concede_button.config(text="Stop Auto Concede")
            self.log_message("Auto Concede activated.")
            self.concede.start()
        else:
            self.auto_concede_active = False
            self.auto_concede_button.config(text="Auto Concede")
            self.log_message("Auto Concede deactivated.")
            self.concede.stop()

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

    def take_region_screenshot(self):
        self.log_message(self.start_x_entry.get())

        if self.start_x_entry.get() and self.start_y_entry.get() and self.width_entry.get() and self.height_entry.get():
            self.bot.capture_region((int(self.start_x_entry.get()), int(self.start_y_entry.get()), int(self.width_entry.get()), int(self.height_entry.get())))
            self.log_message("Region screenshot taken.")