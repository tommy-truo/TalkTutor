"""
Main Application GUI MODULE

This module provides the primary graphical user interface
for the entire application, which integrates all of the
sub-GUIs for the audio recorder, audio transcription, and
AI-response user interfaces.
"""

from recorder_gui import RecorderGUI

import tkinter as tk


class AppGUI:
    def __init__(self, root, app_state):
        self.root = root
        self.root.title("TalkTutor")

        self.app_state = app_state

        self.recorder_gui = RecorderGUI(self.root, self.app_state)

    def run(self):
        self.root.mainloop()