import queue as q
import numpy as np
import threading
import time

class AppState:
    def __init__(self):
        self.audio_data = q.Queue()

        self.is_recording = False
        self.record_start_time = 0.0

        self.transcript = ""
        self.transcribe_start_time = 0.0

        self.lock = threading.Lock()


    # --- Audio Data ---
    def is_audio_empty(self):
        return self.audio_data.empty()
    
    
    def clear_audio_data(self):
        with self.lock:
            while not self.audio_data.empty():
                try:
                    self.audio_data.get_nowait()
                except q.Empty:
                    break

    
    def append_chunk(self, chunk):
        if chunk is not None and len(chunk) > 0:
            if chunk.ndim > 1:
                chunk = chunk.mean(axis=1)

            self.audio_data.put(chunk)
        


    def get_next_chunk(self, timeout=0.5):
        try:
            chunk = self.audio_data.get(timeout=timeout)
            if chunk.ndim > 1:
                chunk.mean(axis=1)
            return chunk
        except q.Empty:
            return None

    
    def get_all_audio(self):
        with self.lock:
            chunks = []
            while not self.audio_data.empty():
                chunks.append(self.audio_data.get())
            
            if chunks:
                return np.concatenate(chunks, axis=0)
            else:
                return np.array([],dtype=np.float32)
        

    # --- Recorder ---
    def set_is_recording(self, value):
        with self.lock:
            self.is_recording = value

    def get_is_recording(self):
        with self.lock:
            return self.is_recording
        
    
    def set_recording_time(self, time):
        with self.lock:
            self.record_start_time = time

    def get_recording_time(self):
        with self.lock:
            return self.record_start_time
        

    # --- Transcriber ---
    def set_transcript(self, text):
        with self.lock:
            if isinstance(text, str):
                self.transcript = text

    def get_transcript(self):
        with self.lock:
            return self.transcript
        

    def append_transcript(self, text):
        with self.lock:
            if isinstance(text, str) and text:
                text = text.strip()

                if self.transcript:
                    self.transcript += " "

                self.transcript += text


    def reset_transcript(self):
        with self.lock:
            self.transcript = ""


    def set_transcribe_time(self, time):
        with self.lock:
            self.transcribe_start_time = time

    def get_transcribe_time(self):
        with self.lock:
            return self.transcribe_start_time


    # --- Utils ---
    def get_elapsed_time(self, start_time):
        with self.lock:
            return time.time() - start_time