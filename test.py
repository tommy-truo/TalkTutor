#temp testing file for any code snippets

from transcriber import Transcriber
from audio_recorder import AudioRecorder
from app_state import AppState
import time

state = AppState()
transcriber = Transcriber(state, model_size="large-v3")
recorder = AudioRecorder(state)


print("starting recorder")
recorder.start()
print("recording...")
time.sleep(15)
recorder.stop()
print("stopped recording")

buffer = state.get_all_audio()
print(f"buffer length: {len(buffer)}")

# Test wrapper transcription
trans_thread = transcriber.start_transcription_thread(buffer=buffer)
trans_thread.join()  # Wait for the transcription thread to finish
print("done transcribing")
print("final transcript: " + state.get_transcript())