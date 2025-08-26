class AppState:
    def __init__(self):
        self.audio_data = None
        self.transcription_text = ""
        self.ai_language = ""
        self.ai_prompt = ""
        self.ai_response = ""

    
    def clear_state(self):
        self.audio_data = None
        self.transcription_text = ""
        self.ai_language = ""
        self.ai_prompt = ""
        self.ai_response = ""


    def set_audio(self, data):
        self.audio_data = data

    
    def get_audio(self):
        return self.audio_data
    

    def set_transcription(self, text):
        self.transcription_text = text

    
    def get_transcription(self):
        return self.transcription_text
    

    def set_ai_prompt(self, text):
        self.ai_prompt = text

    
    def get_ai_prompt(self):
        return self.ai_prompt
    

    def set_ai_language(self, text):
        self.ai_language = text

    
    def get_ai_language(self):
        return self.ai_language
    

    def set_ai_response(self, text):
        self.ai_response = text

    
    def get_ai_response(self):
        return self.ai_response