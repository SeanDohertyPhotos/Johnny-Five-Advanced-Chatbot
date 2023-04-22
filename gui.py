import tkinter as tk
import tkinter.scrolledtext as st
from main import JohnnyFiveChat
import threading

class JohnnyFiveApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Johnny Five Chat")
        self.geometry("800x800")

        # Set dark theme colors
        self.configure(bg="#282828")
        fg_color = "#f0f0f0"

        # Initialize chat object
        self.chat = JohnnyFiveChat()

        # Set up grid layout
        self.grid_rowconfigure(0, weight=4, minsize=120)
        self.grid_rowconfigure(1, weight=1, minsize=60)
        self.grid_columnconfigure(0, weight=1, minsize=180)

        # Create and configure the chat area
        self.chat_area = tk.Text(self, wrap=tk.WORD, state="disabled", bg="#282828", fg=fg_color, font=("Helvetica", 14), spacing1=10, spacing3=10, border=1, borderwidth=1)
        self.chat_area.tag_configure("user", foreground="white", background="#3b3b3b", font=("Helvetica", 14), lmargin1=10, lmargin2=10)
        self.chat_area.tag_configure("johnny_five", foreground="white", background="#172240", font=("Helvetica", 14,), lmargin1=10, lmargin2=10)
        self.chat_area.tag_configure("message", font=("Helvetica", 14))
        self.chat_area.tag_configure("thinking", background="#282828", font=("Helvetica", 14, "italic"))

        # Create a stylized scrollbar for the chat area
        scrollbar = tk.Scrollbar(self, orient="vertical", command=self.chat_area.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.chat_area.config(yscrollcommand=scrollbar.set)

        self.chat_area.grid(row=0, column=0, sticky="nsew", padx=(10, 10), pady=10)

        # Create and configure the input text entry frame
        self.entry_frame = tk.Frame(self, bg="#282828")
        self.entry_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Create and configure the input text entry box using ScrolledText widget
        self.entry_box = st.ScrolledText(self.entry_frame, height=3, wrap=tk.WORD, bg="#282828", fg=fg_color, font=("Helvetica", 12))
        self.entry_box.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Create and configure the "Send" button
        self.send_button = tk.Button(self.entry_frame, text="Send", padx=5, pady=5, command=self.send_text, activebackground="green", bg="#404040", fg=fg_color, font=("Helvetica", 10))
        self.send_button.pack(side=tk.RIGHT)

        # Create and configure the "Toggle TTS" button
        self.tts_button = tk.Button(self.entry_frame, text="Toggle TTS", padx=5, pady=5, command=self.chat.toggle_tts, bg="#404040", fg=fg_color, font=("Helvetica", 10))
        self.tts_button.pack(side=tk.RIGHT, padx=(0, 5))

        # Bind the "Enter" key to the send_text function
        self.entry_box.bind("<Return>", lambda event: self.send_text())

        # Display the introduction message with a delay
        self.after(100, self.send_intro_message)

    def send_intro_message(self):
        intro_message = self.chat.send_message("A new conversation has started, briefly introduce yourself as johnny Five and Advanced Nueral Network creatd by Sean Doherty and then ask who you are speaking to.")
        self.update_chat_area(f"Johnny Five: {intro_message}", "johnny_five")

    def send_text(self):
        user_input = self.entry_box.get("1.0", "end-1c").strip()
        if user_input:
            self.entry_box.delete("1.0", tk.END)
            self.update_chat_area(f"You: {user_input}", "user")
            thinking_text = f"Johnny Five: ...thinking..."
            thinking_id = self.update_chat_area(thinking_text, "thinking")
            threading.Thread(target=self.send_message_thread, args=(user_input, thinking_id)).start()

    def send_message_thread(self, user_input, thinking_id):
        johnny_five_response = self.chat.send_message(user_input)
        self.chat_area.after(10, self.update_chat, thinking_id, f"Johnny Five: {johnny_five_response}", "johnny_five")

    def update_chat(self, thinking_id, text, tag):
        self.remove_thinking(thinking_id)
        self.update_chat_area(text, tag)

    def update_chat_area(self, text, tag):
        self.chat_area.configure(state="normal")
        self.chat_area.insert(tk.END, text + "\n", tag)
        self.chat_area.configure(state="disabled")
        self.chat_area.see(tk.END)
        return self.chat_area.index(tk.END)

    def remove_thinking(self, thinking_id):
        self.chat_area.configure(state="normal")
        self.chat_area.delete(f"{thinking_id} linestart", f"{thinking_id} lineend")
        self.chat_area.configure(state="disabled")

if __name__ == "__main__":
    app = JohnnyFiveApp()
    app.mainloop()

