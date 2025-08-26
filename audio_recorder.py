"""
AUDIO RECORDER MODULE

This module provides the class 'AudioRecorder',
which records audio from a microphone input stream
and returns the captured audio as a NumPy array
to be used for Speech-To-Text.

Features:
    -Records audio in real time with sounddevice.
    -Buffers audio chunks with a thread-safe queue.
    -Returns audio as float32 NumPy array.
    -Can support mono and multi-channel audio recording.
"""


import sounddevice as sd
import numpy as np;
import queue as q;


class AudioRecorder:
    """
    Utility class for capturing audio input from the user's microphone and returning
    it as a NumPy array for use in a speech-to-text module.

    Attributes:
        samplerate (int): The sample rate of the recording in Hz. Default is 16000.
        channels (int): Number of audio channels. Default is 1 (mono).
        audio_queue (queue.Queue): Buffer that stores incoming audio chunks.
        stream (sounddevice.InputStream): The input audio stream from the microphone.
        is_recording (bool): Indicates whether audio is currently being recorded.

    Example:
        recorder = AudioRecorder()
        recorder.start_recording()

        time.sleep(10)  #audio recording is not interrupted by time.sleep()

        recorder.stop_recording()
        audio_data = recorder.get_audio_data()
    """

    def __init__(self, samplerate=16000, channels=1):
        """
        Initialize the audio recorder object.

        Args:
            samplerate (int, optional): The recording's sample rate in Hz. Default is 16000.
            channels (int, optional): The number of audio channels. Default is 1 (mono).
        """

        self.samplerate = samplerate
        self.channels = channels
        self.audio_queue = q.Queue()
        self.stream = None
        self.is_recording = False


    def audio_callback(self, indata, _frames, _time, status):
        """
        Callback function for the audio input stream.

        Callback function to be used by the audio input stream from sounddevice.
        Appends incoming audio chunks to audio_queue.

        Args:
            indata (NumPy.ndarray): Incoming audio chunk from audio input stream.
            _frames (int): Number of frames in the buffer (unused).
            _time (int): Timestamp (unused).
            status: Status of input stream, prints warnings if abnormal status occurs.

        Returns:
            None
        """
        
        if status:
            print(status)

        self.audio_queue.put(indata.astype(np.float32).copy())


    def stop_recording(self):
        """
        Stops capturing audio from the microphone.

        Checks if the microphone is already not recording audio, then stops
        and closes the audio input stream and sets is_recording to False.

        Returns:
            None
        """
        
        if not self.is_recording:
            return
        
        self.stream.stop()
        self.stream.close()

        self.is_recording = False

        print("Stopped recording.")


    def start_recording(self):
        """
        Starts capturing audio from the microphone.

        Closes any currently running audio input stream, then clears the previously
        queued audio chunks, starts a new audio input stream, and sets is_recording
        to True.

        Returns:
            None
        """
        
        if self.is_recording:
            self.stop_recording()
        
        self.audio_queue.queue.clear()

        self.stream = sd.InputStream(
            samplerate=self.samplerate,
            channels=self.channels, 
            dtype='float32',
            callback=self.audio_callback
        )
        
        self.stream.start()
        
        self.is_recording = True

        print("Started recording.")


    def get_audio_data(self):
        """
        Retrieve all stored audio chunks from audio_queue as a NumPy array.

        Closes input stream if it was left open and was still recording.
        Then, it creates and returns a float32 NumPy array containing concatenated
        audio chunks from the audio_queue. Returns an empty NumPy array if no data
        was recorded into the audio_queue.

        Returns:
            NumPy.ndarray: A float32 NumPy array of the concatenated audio chunks
            from the microphone recording that can be played back or used for
            speech-to-text. The array may be empty if no data was stored in
            audio_queue.
        """
        
        if self.is_recording:
            self.stop_recording()
        
        chunks = []
        while not self.audio_queue.empty():
            chunks.append(self.audio_queue.get())
        
        if chunks:
            audio_data = np.concatenate(chunks, axis=0).astype(np.float32)

            if self.channels > 1:
                audio_data = audio_data.flatten()

            return audio_data

        return np.array([], dtype=np.float32)