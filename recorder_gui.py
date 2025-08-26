"""
Recorder Sub-GUI Module

This module provides the RecorderGUI class, which creates a graphical
user interface for recording audio from the user's microphone. It is
designed to be utilized as a subcomponent of a larger main GUI.

Features:
    -Toggle button to start/stop recording audio from user's microphone.
    -Animated status label to display active recording status.
    -Uses separate thread to manage text animation to maintain UI responsiveness.
"""

from audio_recorder import AudioRecorder

import tkinter as tk
import sounddevice as sd
import threading
from time import sleep


class RecorderGUI:
    """
    Sub-GUI for recording audio input from the user's microphone.

    A sub-GUI that is responsible for the audio recorder's user interface.
    Designed to be used as a subcomponent of the larger main GUI.
    """


    def __init__(self, parent, app_state):
        """
        Initializes the RecorderGUI inside of a given parent frame.

        Args:
            parent (tk.Tk): The root window of the application.
        """

        self.parent = parent
        self.app_state = app_state
        self.recorder = AudioRecorder()

        self.frame = tk.Frame(parent)
        self.frame.pack(padx=10, pady=10)

        self.status_label = tk.Label(
            self.frame, 
            text="Not Recording", 
            font=("Arial", 14)
        )
        
        self.status_label.pack(pady=10)

        self.record_button = tk.Button(
            self.frame, 
            text="Start Recording", 
            width=15, 
            command=self.toggle_recording
        )
        self.record_button.pack(pady=10)

        self.recording_animation_running = False

    
    def play_audio(self):
        """
        FOR TESTING PURPOSES ONLY.
        Plays stored audio recording from AppState.

        Returns:
            None
        """

        audio_data = self.app_state.get_audio()
        
        print("Captured audio shape:", audio_data.shape)
        sd.play(audio_data, samplerate=self.recorder.samplerate)  
    
    
    def stop_recording(self):
        """
        Stops ongoing audio recording and updates the audio recorder's UI.

        This stops the audio input stream, updates the record button's text to
        "Start Recording", stops the "Recording..." text animation, and stores
        the recorded audio data from the user's microphone to AppState.

        Returns:
            None
        """
        
        self.recorder.stop_recording()
        self.record_button.config(text="Start Recording")
        self.recording_animation_running = False

        audio_data = self.recorder.get_audio_data()
        self.app_state.set_audio(audio_data)


    def start_recording(self):
        """
        Starts audio recording and updates the audio recorder's UI.

        This opens the audio input stream, updates the record button's text to
        "Stop Recording", starts the "Recording..." text animation, and runs
        that text animation in a separate thread to prevent making the UI
        unresponsive.

        Returns:
            None
        """
        
        self.recorder.start_recording()
        self.record_button.config(text="Stop Recording")
        self.recording_animation_running = True
            
        threading.Thread(target=self.recording_animation, daemon=True).start()

    
    def toggle_recording(self):
        """
        Controls the behavior of the record button's behavior depending on
        whether the audio input stream is open or closed.

        Checks to see if audio is currently being recorded, and if so, will
        stop the recording and play back the audio. Otherwise, it starts a
        new recording session.

        Returns:
            None
        """
        
        if self.recorder.is_recording:
            self.stop_recording()

            self.play_audio()
        else:
            self.start_recording()

    
    def recording_animation(self):
        """
        Controls the status label animation during a recording session.

        Displays an endless animation cycle of "Recording", "Recording.",
        "Recording..", and "Recording..." on the recording session status
        label only when a recording session is in progress.

        Returns:
            None
        """
        
        animation_states = [
            "Recording", 
            "Recording.", 
            "Recording..", 
            "Recording..."
            ]
        
        i = 0
        while self.recording_animation_running:
            self.status_label.config(
                text=animation_states[i % len(animation_states)])
            i += 1
            sleep(0.25)
        else:
            self.status_label.config(text="Not Recording")