import sounddevice as sd
import numpy as np
import time


class AudioRecorder:
    def __init__(self, state, samplerate=16000, channels=1):
        self.state = state
        self.samplerate = samplerate
        self.channels = channels
        
        self.stream = None

    
    def audio_callback(self, indata, frames, time, status):
        if status:
            print(status)

        self.state.append_chunk(indata.copy())


    def start(self):
        if not self.state.is_audio_empty():
            self.state.clear_audio_data()
        
        self.stream = sd.InputStream(
            samplerate=self.samplerate,
            channels=self.channels,
            blocksize=320,
            dtype="float32",
            callback=self.audio_callback
        )

        self.state.set_recording_time(time.time())
        self.stream.start()
        self.state.set_is_recording(True)


    def stop(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()
        
        self.state.set_is_recording(False)


    def play_audio(self):
        audio = self.state.get_all_audio()
        
        print("Captured audio shape:", audio.shape)
        sd.play(audio, samplerate=self.samplerate)