from faster_whisper import WhisperModel
from torch import cuda
import numpy as np
import queue as q
import time


class Transcriber:
    def __init__(self, audio_queue=None, output_queue=None,
                 max_model_size="large-v3", min_model_size = "small", 
                 audio_samplerate=16000, chunk_duration=2):
        self.audio_queue = audio_queue if audio_queue is not None else q.Queue()
        self.output_queue = output_queue if output_queue is not None else q.Queue()
        
        self.max_model_size = max_model_size
        self.min_model_size = min_model_size
        self.device = "cuda" if cuda.is_available() else "cpu"
        self.model = self.create_model(self.max_model_size)

        self.audio_samplerate = audio_samplerate
        self.chunk_duration = chunk_duration


    def create_model(self, model_size):
        VALID_MODELS = [
        "tiny", "tiny.en", 
        "base", "base.en", 
        "small", "small.en", 
        "medium", "medium.en", 
        "large-v1", 
        "large-v2", 
        "large-v3"
        ]

        if model_size not in VALID_MODELS:
            raise ValueError(f"Invalid model size '{model_size}'. Valid options are: {', '.join(VALID_MODELS)}")
            
        if cuda.is_available():
            print("Creating Transcriber model utilizing CUDA.")
            model = WhisperModel(model_size, device="cuda", compute_type="float32")
        else:
            print("Creating Transcriber model utilizing CPU.")
            index = VALID_MODELS.index(model_size)
            if index < VALID_MODELS.index("large-v1"):
                model = WhisperModel(model_size, device="cpu", compute_type="int8")
            else:
                print("Model size '" + model_size + "' is too large for CPU computation. Using '" + self.min_model_size + "' instead.")
                model = WhisperModel(self.min_model_size, device="cpu", compute_type="int8")
        
        print("Created Transcriber model.")

        return model


    def clear_buffer(self):
        self.buffer = np.zeros(0, dtype=np.float32)
    
    
    def transcribe(self, audio):
        if len(audio) > 0 and audio is not None:
            segments, info = self.model.transcribe(
                audio=audio,
                no_repeat_ngram_size=2,
                vad_filter=True
            )
            transcribed_words = []
            
            for segment in segments:
                if segment.no_speech_prob < 0.7:
                    transcribed_words.append(segment.text)

            output_string = " ".join([word for word in transcribed_words])
                
            return output_string


    def transcribe_to_queue(self, audio, output_queue=None):
        if output_queue is None:
            output_queue = self.output_queue
        
        if len(audio) > 0 and audio is not None:
            segments, info = self.model.transcribe(
                audio=audio,
                no_repeat_ngram_size=2,
                vad_filter=True
            )
            
            for segment in segments:
                if segment.no_speech_prob < 0.7:
                    self.output_queue.put(segment.text)

            return self.output_queue
    

    def live_transcribe(self, audio_queue=None, output_queue=None):
        if audio_queue is None:
            audio_queue = self.audio_queue
        if output_queue is None:
            output_queue = self.output_queue

        buffer = []
        accumulated_samples = 0
        chunk_size = self.chunk_duration * self.audio_samplerate

        transcribed_words = []

        while True:
            try:
                chunk = audio_queue.get(timeout=self.chunk_duration*3)  #wait for an audio chunk
            except q.Empty:
                print("Warning: Failed to get chunk from audio queue. Ending transcription.")
                break

            if chunk is None:
                break #None is the stop signal for audio recording

            buffer.append(chunk)
            accumulated_samples += chunk.shape[0]

            if accumulated_samples >= chunk_size:
                concatenated_buffer = np.concatenate(buffer, axis=0)
                audio_to_transcribe = concatenated_buffer[:chunk_size]
                leftover_audio = concatenated_buffer[chunk_size:]

                buffer = [leftover_audio] if leftover_audio.size > 0 else []
                accumulated_samples = leftover_audio.shape[0]

                segments, info = self.model.transcribe(
                    audio=audio_to_transcribe,
                    no_repeat_ngram_size=2,
                    vad_filter=True
                )
            
                for segment in segments:
                    if segment.no_speech_prob < 0.7:
                        self.output_queue.put(segment.text)
                        transcribed_words.append(segment.text)

        return self.output_queue