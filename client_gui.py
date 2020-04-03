import json
import os
import time
from datetime import datetime
from threading import Thread
from tkinter import Button, Entry, Frame, Label, Tk, font
from tkinter.scrolledtext import ScrolledText

from irc_client import IRCClient


class ChatClientGUI(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.master = master
        self.master.protocol("WM_DELETE_WINDOW", self.close_window)
        self.master.title("Chat Client GUI")
        self.pack(fill="both", expand=True)
        self.font = font.Font(font=("Helvetica Neue", 12))
        self.background_color = "#333333"
        self.box_background_color = "#655F5F"
        self.text_color = "#FFFFFF"
        
        # Build the chat
        self.chat_frame = Frame(self)
        self.chat_frame.pack(fill="both", expand=True, anchor="nw")
        self.chat_frame.configure(bg=self.background_color)
        self.chat_box = ScrolledText(self.chat_frame, font=self.font, wrap="word")
        self.chat_box.configure(state="disabled", bg=self.box_background_color, fg=self.text_color)
        self.chat_box.pack(side="left", fill="both", expand=True, padx=5, pady=5, anchor="nw")
        
        # Users list
        self.users_label = Label(self.chat_frame, text="Users in Channel", bg=self.background_color, fg=self.text_color, font=font.Font(font=("Helvetica Neue", 12, "bold")))
        self.users_label.pack(side="top", anchor="n")
        self.users_box = ScrolledText(self.chat_frame, font=self.font, width=25)
        self.users_box.configure(state="disabled", bg=self.box_background_color, fg=self.text_color)
        self.users_box.pack(side="right", fill="y", padx=5, pady=5, anchor="ne")
        
        # Build the input section
        self.input_frame = Frame(self, height=1)
        self.input_frame.pack(side="bottom", fill="x", anchor="sw")
        self.input_frame.configure(bg=self.background_color)
        self.chat_input = Entry(self.input_frame, font=self.font)
        self.chat_input.configure(bg=self.box_background_color, fg=self.text_color, insertbackground=self.text_color)
        self.chat_input.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        self.chat_input.bind("<Return>", self.send_message_on_return)
        self.send_button = Button(self.input_frame, text="Send", width=10, command=self.send_message, bg=self.box_background_color, fg=self.text_color)
        self.send_button.pack(side="right", fill="x", padx=5, pady=5)
        
        # Update the window and then set the minsize
        self.master.update()
        self.master.minsize(self.master.winfo_width(), self.master.winfo_height())
        
        # Non tkinter class variables
        self.instance = None
        self.running = True
        
        # Spawn threads used for chat client and channel users fetch
        self.chat_client_thread = Thread(target=self.start_chat_client)
        self.chat_client_thread.start() 
        self.users_fetch = Thread(target=self.get_users)
        self.users_fetch.start()
        
    def send_message(self):
        message = self.chat_input.get()
        self.instance.send_privmsg(message)
        self.write_to_chatbox(message, self.instance.client_username)
        self.chat_input.delete(0, "end")
        
    def send_message_on_return(self, event):
        # Forward to the send message handler (to get around needing the "event" parameter)
        self.send_message()
        del event

    def write_to_chatbox(self, msg, username):
        date = f"[{datetime.now():%I:%M:%S}] "
        formatted_message = f"{date} {username}: {msg}"
        self.chat_box.configure(state="normal")
        self.chat_box.insert("end", formatted_message + "\n")
        self.chat_box.see("end")
        self.chat_box.configure(state="disabled")
        
    def write_many(self, msg, times):
        for _ in range(times):
            self.write_to_chatbox(msg)
    
    def start_chat_client(self):
        with open("settings.json", "r") as r:
            settings = json.load(r)
            username = settings["username"]
            token = settings["token"]
            channel = settings["channel"]
            server = settings["server"]
            port = settings["port"]
        self.instance = IRCClient(username, token, channel, server, port, settings, self)
        self.instance.start()
    
    def get_users(self):
        while self.running:
            time.sleep(5)
            users = self.instance.channels.get(self.instance.channel).users()
            self.users_box.configure(state="normal")
            self.users_box.delete('1.0', 'end')
            for user in users:
                self.users_box.insert('end', user + "\n")
            self.users_box.configure(state="disabled")
            
    def close_window(self):
        self.running = False
        self.instance.disconnect()
        os._exit(0)


def main():
    root = Tk()
    gui = ChatClientGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
