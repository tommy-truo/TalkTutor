from llama_cpp import Llama
import os

class LLM:
    def __init__(self, state, response_lang="English", gpu_layers=6, n_ctx=8192):
        self.state = state
        self.response_lang = response_lang
        
        model_folder = "models/qwen2.5-7b-instruct"
        base_dir = os.path.dirname(os.path.abspath(__file__))
        first_file = os.path.join(base_dir, model_folder, "qwen2.5-7b-instruct-q4_k_m-00001-of-00002.gguf")

        self.convo_prompt = f"You are TalkTutor, a friendly conversation partner chatbot. No matter what the user says, reply naturally in {self.response_lang}."
        self.llm_intro = "Hello! I am TalkTutor, your conversation coach! Please begin recording to start."

        self.chat_history = [
            {"role": "system", "content": self.convo_prompt},
        ]
        
        self.llm = Llama(
            model_path=first_file,
            n_ctx=n_ctx,
            n_threads=os.cpu_count(),
            n_gpu_layers=gpu_layers
        )

        print("LLM loaded")
    
    
    def append_chat(self, role, content):
        self.chat_history.append({"role":role, "content":content})
    
    
    def translate(self, sentence):
        prompt = f"Generate a translation of the following in {self.response_lang} '{sentence}'. Do not generate any other text. If the sentence is already in {self.response_lang}, just generate the sentence again."

        output = self.llm(
            prompt, 
            temperature=0.0,
            max_tokens=100,
        )
        
        return output['choices'][0]['text'].strip()

    
    def generate_translated_intro(self):
        prompt = f"Generate a translation of the following sentence in {self.response_lang} '{self.llm_intro}'. Do not generate any other text. If the sentence is already in {self.response_lang}, just generate the sentence again."

        output = self.llm(
            prompt, 
            temperature=0.0,
            max_tokens=100,
        )
        
        return output['choices'][0]['text'].strip()

    
    def generate_correct_sentence(self, sentence):
        prompt = f"Only generate a grammatically correct version of the given sentence '{sentence}'. Do not generate any text about what you changed. Ignore all punctuation and capitalization errors."

        output = self.llm(
            prompt,
            temperature=0.0,
            max_tokens=500
        )

        return output['choices'][0]['text'].strip()
    

    def generate_summarized_sentence(self, sentence):
        prompt = f"Summarize the following sentence in 20 words or less without changing the original meaning: '{sentence}'. Do not generate any text about what you changed."
        
        output = self.llm(
            prompt, 
            temperature=0.0,
            max_tokens=100,
        )
        
        return output['choices'][0]['text'].strip()
    

    def generate_convo_response(self, sentence):      
        self.append_chat("user", self.generate_summarized_sentence(sentence))
        
        output = self.llm.create_chat_completion(
            messages=self.chat_history,
            temperature=0.7,
            max_tokens=100
        )

        self.append_chat("assistant", output['choices'][0]['message']['content'])
        
        return output['choices'][0]['message']['content']