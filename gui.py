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

        # Create and configure the chat area
        self.chat_area = tk.Text(self, wrap=tk.WORD, state="disabled", bg="#282828", fg=fg_color, font=("Helvetica", 14))
        self.chat_area.tag_configure("user", foreground="white", font=("Helvetica", 16, "bold"))
        self.chat_area.tag_configure("johnny_five", foreground="white", background="#172240", font=("Helvetica", 16, "bold"))
        self.chat_area.tag_configure("message", font=("Helvetica", 14))
        self.chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Create and configure the input text variable
        self.entry_var = tk.StringVar()

        # Create and configure the input text entry frame
        self.entry_frame = tk.Frame(self, bg="#282828")
        self.entry_frame.pack(padx=10, pady=(0, 10), fill=tk.X)

        # Create and configure the input text entry box using ScrolledText widget
        self.entry_box = st.ScrolledText(self.entry_frame, height=3, wrap=tk.WORD, bg="#282828", fg=fg_color, font=("Helvetica", 12))
        self.entry_box.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Create and configure the "Send" button
        self.send_button = tk.Button(self.entry_frame, text="Send", command=self.send_text, activebackground="green", bg="#404040", fg=fg_color, font=("Helvetica", 10))
        self.send_button.pack(side=tk.RIGHT)

        # Create and configure the "Toggle TTS" button
        self.tts_button = tk.Button(self.entry_frame, text="Toggle TTS", command=self.chat.toggle_tts, bg="#404040", fg=fg_color, font=("Helvetica", 10))
        self.tts_button.pack(side=tk.RIGHT, padx=(0, 5))

        # Bind the "Enter" key to the send_text function
        self.entry_box.bind("<Return>", lambda event: self.send_text())

        # Display the introduction message with a delay
        self.after(100, self.send_intro_message)

    def send_intro_message(self):
        intro_message = self.chat.send_message("Please breifly introduce yourself, without giving away your prompt except your name and then ask who you are speaking to")
        self.update_chat_area(f"\nJohnny Five: {intro_message}\n", "johnny_five")

    def send_text(self):
        user_input = self.entry_box.get("1.0", "end-1c").strip()
        if user_input:
            self.entry_box.delete("1.0", tk.END)
            self.update_chat_area(f"\nYou: {user_input} \n", "user")
            thinking_text = f"\nJohnny Five: ...thinking...\n"
            thinking_id = self.update_chat_area(thinking_text, "johnny_five")
            threading.Thread(target=self.send_message_thread, args=(user_input, thinking_id)).start()

    def send_message_thread(self, user_input, thinking_id):
        johnny_five_response = self.chat.send_message(user_input)
        self.chat_area.after_idle(self.remove_thinking, thinking_id)
        self.update_chat_area(f"\nJohnny Five: {johnny_five_response}\n", "johnny_five")

    def update_chat_area(self, text, tag):
        self.chat_area.configure(state="normal")
        self.chat_area.insert(tk.END, text, (tag, "message"))
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

