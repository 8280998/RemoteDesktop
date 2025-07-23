import socket
import pickle
import struct
import tkinter as tk
from PIL import Image, ImageTk
import threading
import time

HOST = '服务器IP地址'  # 替换为服务器的IP
PORT = 5000

class RemoteDesktop(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Remote Desktop")
        self.canvas = tk.Canvas(self, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HOST, PORT))
        self.bind_events()
        threading.Thread(target=self.receive_screen, daemon=True).start()

    def receive_screen(self):
        while True:
            try:
                # 接收图像大小
                data_len = struct.unpack("Q", self.sock.recv(8))[0]
                data = b''
                while len(data) < data_len:
                    packet = self.sock.recv(data_len - len(data))
                    if not packet:
                        return
                    data += packet
                img_data = pickle.loads(data)
                img = Image.open(io.BytesIO(img_data))
                self.photo = ImageTk.PhotoImage(img)
                self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
                time.sleep(0.05)
            except Exception as e:
                print(f"Error: {e}")
                break

    def bind_events(self):
        self.canvas.bind("<Motion>", self.send_mouse_move)
        self.canvas.bind("<Button-1>", self.send_click)
        self.bind("<Key>", self.send_key)

    def send_mouse_move(self, event):
        data = pickle.dumps({'type': 'mouse', 'x': event.x, 'y': event.y})
        self.sock.sendall(data)

    def send_click(self, event):
        data = pickle.dumps({'type': 'click'})
        self.sock.sendall(data)

    def send_key(self, event):
        data = pickle.dumps({'type': 'key', 'key': event.keysym})
        self.sock.sendall(data)

if __name__ == "__main__":
    app = RemoteDesktop()
    app.mainloop()
