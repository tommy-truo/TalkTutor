from app_state import AppState
from audio_recorder import AudioRecorder
from transcriber import Transcriber

import threading


class Controller:
    def __init__(self):
        self.state = AppState()
        self.recorder = AudioRecorder(self.state)
        self.transcriber = Transcriber(self.state)

    
    # --- Recorder ---
    def start_recording(self):
        self.recorder.start()


    def stop_recording(self):
        self.recorder.stop()


    def get_audio_data(self):
        return self.state.get_all_audio()
    
    
    def play_audio(self):
        self.recorder.play_audio()


    def get_is_recording(self):
        return self.state.get_is_recording()
    

    def get_elapsed_record_time(self):
        return self.state.get_elapsed_time(self.state.get_recording_time())


    def toggle_recording(self):
        if self.state.get_is_recording():
            self.stop_recording()
            #self.wait_for_transcription()
        else:
            self.start_recording()
            self.start_transcribing()


    # --- Transcriber ---
    def get_transcript(self):
        return self.state.get_transcript()
    
    
    def get_elapsed_transcribe_time(self):
        return self.state.get_elapsed_time(self.state.get_transcribe_time())
    

    def start_transcribing(self):
        return self.transcriber.start_transcription_thread()
    
    def get_transcription_thread(self):
        return self.transcriber.get_thread()
    

    def wait_for_transcription(self):
        transcription_thread = self.get_transcription_thread()
        if transcription_thread is not None:
            transcription_thread.join()