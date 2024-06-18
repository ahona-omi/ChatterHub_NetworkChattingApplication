import socket
import tkinter as tk
import threading
import os
import tkinter.filedialog as tkfiledialog
import time
from PIL import Image, ImageTk

class ServerGUI:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.ServerSocket = None
        self.connections = []

        self.root = tk.Tk()
        self.root.title("ChatterHub-Server")
        self.root.configure(bg="#033043")

        background_image = Image.open("background.jpg")
        background_image = background_image.resize((950, 920), Image.LANCZOS)
        self.background_photo = ImageTk.PhotoImage(background_image)

        # Create a label to display the background image
        self.background_label = tk.Label(self.root, image=self.background_photo)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.messages_frame = tk.Frame(self.root, bg="#033043")
        self.messages_frame.pack(padx=10, pady=10)

        self.messages_scrollbar = tk.Scrollbar(self.messages_frame, bg="#033043")
        self.messages_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.messages = tk.Text(self.messages_frame, height=30, width=60, bg="#e9e3d5", fg="#033043",
                                yscrollcommand=self.messages_scrollbar.set, font="Nunito")
        self.messages.pack()
        self.messages_scrollbar.config(command=self.messages.yview)

        self.entry = tk.Entry(self.root, width=65, bg="#033043", fg="#e9e3d5")
        self.entry.pack(side=tk.LEFT, pady=5)

        self.send_button = tk.Button(self.root, text="Send Message", command=self.send_message, bg="#033043", fg="#e9e3d5",
                                     relief=tk.FLAT)
        self.send_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.file_button = tk.Button(self.root, text="Choose File", command=self.send_file, bg="#033043", fg="#e9e3d5",
                                     relief=tk.FLAT)
        self.file_button.pack(pady=5)

        threading.Thread(target=self.setup_server).start()


    def setup_server(self):
        self.ServerSocket = socket.socket()
        self.ServerSocket.bind((self.host, self.port))
        self.ServerSocket.listen(5)

        while True:
            connection, address = self.ServerSocket.accept()
            self.connections.append(connection)
            threading.Thread(target=self.receive_message, args=(connection,)).start()

    def receive_message(self, connection):
        while True:
            try:
                data = connection.recv(1024).decode()
                if data:
                    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                    sender_name, message = data.split(":", 1)
                    message_with_time = f'[{current_time}] {sender_name}: {message}'
                    self.messages.insert(tk.END, message_with_time + '\n')
                    # Broadcast the message to all connected clients
                    for conn in self.connections:
                        if conn != connection:  # Don't send the message back to the sender
                            conn.send(data.encode())
                    if message.startswith("FILE:"):
                        filename = message.split(":")[1]
                        self.receive_file(connection, filename)
            except Exception as e:
                print(e)
                break

    def receive_file(self, connection, filename):
        try:
            with open(filename, "wb") as file:
                while True:
                    data = connection.recv(1024)
                    if not data:
                        break
                    file.write(data)
            self.messages.insert(tk.END, 'File received: ' + filename + '\n')
        except Exception as e:
            print(e)

    def send_message(self):
        message = self.entry.get()
        if message:
            current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            message_with_time = f'[{current_time}] Me: {message}'
            self.messages.insert(tk.END, message_with_time + '\n')
            for connection in self.connections:
                connection.send((message).encode())
            self.entry.delete(0, tk.END)

    def send_file(self):
        filename = tkfiledialog.askopenfilename()
        if filename:
            for connection in self.connections:
                connection.send(("FILE:" + os.path.basename(filename)).encode())
                with open(filename, "rb") as file:
                    data = file.read(1024)
                    while data:
                        connection.send(data)
                        data = file.read(1024)
            self.messages.insert(tk.END, 'File sent: ' + os.path.basename(filename) + '\n')


if __name__ == "__main__":
    server_gui = ServerGUI("127.0.0.1", 1334)
    server_gui.root.mainloop()
