import sounddevice as sd
import numpy as np
import queue as q


class AudioRecorder:
    def __init__(self, audio_queue=None,
                 samplerate=16000, blocksize = 4096, channels=1, dtype='float32', latency='low'):
        self.samplerate = samplerate
        self.channels = channels
        self.blocksize = blocksize
        self.dtype = dtype
        self.latency = latency

        self.audio_queue = audio_queue if audio_queue is not None else q.Queue() #use class-level queue if external queue is not provided
        self.using_internal_queue = audio_queue is None

        self.stream = None

    
    #clears internal audio queue
    def clear_queue(self):
        if self.using_internal_queue:
            while not self.audio_queue.empty():
                self.audio_queue.get_nowait()

    
    def append_chunk(self, chunk):
        if chunk is not None:
            if chunk.ndim > 1:
                chunk = chunk.mean(axis=1)

            self.audio_queue.put(chunk)

    
    def audio_callback(self, indata, frames, time, status):
        #for testing and debugging
        #if status:
            #print(status)

        self.append_chunk(indata.copy())


    def start(self):    
        if self.stream is None:
            self.stream = sd.InputStream(
                samplerate=self.samplerate,
                blocksize=self.blocksize,
                channels=self.channels,
                dtype=self.dtype,
                latency=self.latency,
                callback=self.audio_callback
            )

            self.stream.start()

    
    def stop(self):
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
            self.stream = None

            self.audio_queue.put(None)

    
    def get_all_chunks(self):
        chunks = []
        while not self.audio_queue.empty():
            chunk = self.audio_queue.get()

            if chunk is not None:
                chunks.append(chunk)

        #restore audio_queue to preserve data
        for chunk in chunks:
            self.audio_queue.put(chunk)
            
        if chunks:
            return np.concatenate(chunks, axis=0)
        else:
            return np.array([],dtype=np.float32)


    #for testing purposes
    #only plays audio if stream is not active
    def play_audio(self):
        if self.stream is None:
            audio = self.get_all_chunks()
            
            print("Captured audio shape:", audio.shape)
            sd.play(audio, samplerate=self.samplerate)