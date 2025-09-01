from gui.recorder_frame import RecorderFrame
from gui.transcriber_frame import TranscriberFrame

import tkinter as tk
import threading

class AppGUI:
    def __init__(self, root, controller):
        self.root = root
        self.root.title("TalkTutor")
        self.controller = controller

        # Upper frame to hold left & right panels
        self.upper_frame = tk.Frame(self.root)
        self.upper_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # left panel placeholder (for now)
        self.transcriber_frame = TranscriberFrame(self.upper_frame, self.controller)
        self.transcriber_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Right panel placeholder (for now)
        self.response_frame = tk.Frame(self.upper_frame, bg="lightgray", width=200)
        self.response_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Recorder GUI at bottom
        self.recorder_gui = RecorderFrame(self.root, self.controller)
        self.recorder_gui.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
    
    
    def run(self):
        self.root.mainloop()