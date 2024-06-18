import socket
import tkinter as tk
import threading
from PIL import Image, ImageTk
import time

class ClientGUI:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None
        self.client_name = None
        self.sending_file = False  # Flag to indicate if a file is being sent

        self.root = tk.Tk()
        self.root.title("ChatterHub-Client")
        self.root.configure(bg="#190019")

        background_image = Image.open("images.jpg")
        background_image = background_image.resize((760, 790), Image.LANCZOS)
        self.background_photo = ImageTk.PhotoImage(background_image)

        # Create a label to display the background image
        self.background_label = tk.Label(self.root, image=self.background_photo)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.name_label = tk.Label(self.root, text="Add your name:", bg="#190019", fg="#fbe4db")
        self.name_label.pack(padx=10, pady=5)
        self.name_entry = tk.Entry(self.root, width=30, bg="#190019", fg="#fbe4db")
        self.name_entry.pack(padx=10, pady=5)
        self.name_button = tk.Button(self.root, text="Submit", command=self.set_client_name, bg="#190019",
                                     fg="#fbe4db", relief=tk.FLAT)
        self.name_button.pack(padx=10, pady=5)

        self.messages_frame = tk.Frame(self.root)
        self.messages_frame.pack(padx=10, pady=10)

        self.messages_scrollbar = tk.Scrollbar(self.messages_frame, bg="#190019")
        self.messages_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.messages = tk.Text(self.messages_frame, height=25, width=60, bg="#fbe4db", fg="#190019",
                                yscrollcommand=self.messages_scrollbar.set, font="Roboto")
        self.messages.pack()
        self.messages_scrollbar.config(command=self.messages.yview)

        self.entry = tk.Entry(self.root, width=60, bg="#190019", fg="#fbe4db")
        self.entry.pack(side=tk.LEFT, pady=5)

        self.send_button = tk.Button(self.root, text="Send Message", command=self.send_message, bg="#190019",
                                     fg="#fbe4db", relief=tk.FLAT)
        self.send_button.pack(side=tk.LEFT, padx=5, pady=5)

        threading.Thread(target=self.setup_client).start()

    def set_client_name(self):
        name = self.name_entry.get().strip()
        if name:
            self.client_name = name
            self.name_label.destroy()
            self.name_entry.destroy()
            self.name_button.destroy()
            self.name_label = tk.Label(self.messages_frame, text="Your name: " + self.client_name, bg="#fbe4db",
                                       fg="#190019")
            self.name_label.pack(padx=10, pady=5)
            self.entry.focus_set()

    def setup_client(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        threading.Thread(target=self.receive_message).start()

    def receive_message(self):
        while True:
            try:
                data = self.socket.recv(1024).decode()
                if data:
                    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                    self.messages.insert(tk.END, f'[{current_time}] Server: {data}\n')
                    if data.startswith("FILE:"):
                        filename = data.split(":")[1]
                        self.receive_file(filename)
            except Exception as e:
                print(e)
                break

    def receive_file(self, filename):
        try:
            save_filename = "received_" + filename
            with open(save_filename, "wb") as file:
                while True:
                    data = self.socket.recv(1024)
                    if not data:
                        break
                    file.write(data)
            self.messages.insert(tk.END, 'File received from Server: ' + save_filename + '\n')
        except Exception as e:
            print(e)

    def send_message(self):
        if not self.sending_file:        # Don't send message if sending a file
            message = self.entry.get()
            if message:
                full_message = f'{self.client_name}: {message}'
                self.messages.insert(tk.END, 'Me: ' + message + '\n')
                self.socket.send(full_message.encode())
                self.entry.delete(0, tk.END)


if __name__ == "__main__":
    client_gui = ClientGUI("127.0.0.1", 1334)
    client_gui.root.mainloop()

