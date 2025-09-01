import tkinter as tk


class TranscriberFrame(tk.Frame):
    def __init__(self, parent, controller, poll_interval=1000):
        super().__init__(parent)
        self.controller = controller
        self.poll_interval = poll_interval

        self.last_transcript = ""
        
        self.text_widget = tk.Text(self, wrap="word", state="disabled")
        self.text_widget.pack(expand=True, fill="both")
        
        self.poll_transcript()


    def poll_transcript(self):
        transcript = self.controller.get_transcript()

        if transcript != self.last_transcript:
            self.last_transcript = transcript
            self.text_widget.config(state="normal")
            self.text_widget.delete("1.0", tk.END)
            self.text_widget.insert(tk.END, transcript)
            self.text_widget.config(state="disabled")

        self.after(self.poll_interval, self.poll_transcript)