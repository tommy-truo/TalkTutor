from gui.app_gui import AppGUI
from controller import Controller
import tkinter as tk

import time

def main():
    root = tk.Tk()
    controller = Controller()
    app = AppGUI(root, controller)
    app.run()
    


if __name__ == "__main__":
    main()