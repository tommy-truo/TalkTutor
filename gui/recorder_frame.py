import tkinter as tk


class RecorderFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.pack(padx=10, pady=10)

        self.status_label = tk.Label(self, text="Not Recording", fg="red")
        self.status_label.pack(pady=10)

        self.record_button = tk.Button(
            self,
            text="Start Recording",
            width=15,
            command=self.on_button_click
        )
        self.record_button.pack(pady=10)

        self.update_timer()


    def on_button_click(self):
        self.controller.toggle_recording()

        if self.controller.get_is_recording():
            self.record_button.config(text="Stop Recording")
        else:
            self.record_button.config(text="Start Recording")


    def update_timer(self):
        if self.controller.get_is_recording():
            elapsed = self.controller.get_elapsed_record_time()
            mins = int(elapsed // 60)
            secs = int(elapsed % 60)

            formatted_time = f"{mins:02d}:{secs:02d}"
            self.status_label.config(text=formatted_time, fg="red")
        else:
            self.status_label.config(text="Not Recording", fg="red")
        
        self.after(500, self.update_timer)
