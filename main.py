from app_gui import AppGUI
from app_state import AppState
import tkinter as tk

def main():
    root = tk.Tk()
    app_state = AppState()
    app = AppGUI(root, app_state)
    app.run()

if __name__ == "__main__":
    main()