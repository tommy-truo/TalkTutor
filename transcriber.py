from faster_whisper import WhisperModel
from torch import cuda
import threading
import numpy as np
import time


class Transcriber:
    def __init__(self, state, model_size="large-v3", samplerate=16000, 
                 chunk_duration=3):
        self.state = state
        self.device_type = "cuda" if cuda.is_available() else "cpu"
        self.model = self.create_model(model_size)
        self.samplerate = samplerate

        self.buffer = np.zeros(0, dtype=np.float32)

        self.chunk_duration = chunk_duration

        self.chunk_buffer_size = chunk_duration * samplerate

        self.last_end_time = 0.0
        self.time_offset = 0.0

        self.transcription_thread = None


    def create_model(self, model_size):
        MODEL_ORDER = [
        "tiny", "tiny.en", 
        "base", "base.en", 
        "small", "small.en", 
        "medium", "medium.en", 
        "large-v1", 
        "large-v2", 
        "large-v3"
        ]

        if model_size not in MODEL_ORDER:
            raise ValueError(f"Invalid model size '{model_size}'. Valid options are: {', '.join(MODEL_ORDER)}")
            
        if cuda.is_available():
            print("using cuda")
            model = WhisperModel(model_size, device="cuda", compute_type="float32")
            print("created model using cuda")
        else:
            print("using cpu")
            index = MODEL_ORDER.index(model_size)
            if index < MODEL_ORDER.index("medium"):
                model = WhisperModel(model_size, device="cpu", compute_type="int8")
            else:
                print("Model size '" + model_size + "' is too large for CPU computation. Using 'small' instead.")
                model = WhisperModel("small", device="cpu", compute_type="int8")
            print("created model using cpu")

        return model
    

    def clear_buffer(self):
        self.buffer = np.zeros(0, dtype=np.float32)

    def reset_times(self):
        self.last_end_time = 0.0
        self.time_offset = 0.0

    def reset_state(self):
        self.clear_buffer()
        self.reset_times()
        self.state.reset_transcript()
    
    
    def transcribe_batch(self, buffer=None):
        if buffer is None:
            buffer = self.buffer
        
        if len(buffer) > 0:
            segments, info = self.model.transcribe(buffer)
            transcribed_text = " ".join([segment.text for segment in segments])
            self.state.append_transcript(transcribed_text)


    def transcribe_chunked(self, buffer=None):
        if buffer is None:
            buffer = self.buffer

        while len(buffer) >= self.chunk_buffer_size:
            chunk_to_process = buffer[:self.chunk_buffer_size]
            buffer = buffer[self.chunk_buffer_size:]

            segments, info = self.model.transcribe(chunk_to_process)

            for segment in segments:
                if hasattr(segment, "avg_logprob") and hasattr(segment, "compression_ratio"):
                    if segment.avg_logprob < -1.0 or segment.compression_ratio > 2.4:
                        continue
                
                absolute_start = segment.start + self.time_offset
                absolute_end = segment.end + self.time_offset

                if absolute_start >= self.last_end_time:
                    self.state.append_transcript(segment.text)
                    self.last_end_time = absolute_end

            self.time_offset += (self.chunk_buffer_size) / self.samplerate

        return buffer
    

    def transcribe_wrapper(self, buffer=None):
        if buffer is None:
            buffer = self.buffer

        self.reset_times()
        self.state.reset_transcript()

        while self.state.get_is_recording() or not self.state.is_audio_empty():
            chunk = self.state.get_next_chunk(timeout=0.5)

            if chunk is not None and len(chunk) > 0:
                buffer = np.concatenate([buffer, chunk])
            
            while len(buffer) >= self.chunk_buffer_size:
                buffer = self.transcribe_chunked(buffer)
            
            time.sleep(0.01)

        if len(buffer) > 0:
            self.transcribe_batch(buffer)


    def start_transcription_thread(self, buffer=None):
        if self.transcription_thread is not None and self.transcription_thread.is_alive():
            print("Transcription thread is already running.")
            return self.transcription_thread
        
        self.reset_state()
        thread = threading.Thread(target=self.transcribe_wrapper, args=(buffer,), daemon=True)
        self.state.set_transcribe_time(time.time())
        thread.start()
        self.transcription_thread = thread


    def get_thread(self):
        return self.transcription_thread