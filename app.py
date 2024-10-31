import tkinter as tk
from ui import BotUI
from app_state import AppState

if __name__ == "__main__":
    root = tk.Tk()
    app_state = AppState()
    ui = BotUI(root, app_state)
    root.mainloop()