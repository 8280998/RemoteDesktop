import socket
import mss
import mss.tools
import pyautogui
import pickle
import struct
import threading
import time

HOST = '0.0.0.0'  # 监听所有IP
PORT = 5000       # 端口

def capture_screen():
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # 主屏幕
        img = sct.grab(monitor)
        return mss.tools.to_png(img.rgb, img.size)

def handle_client(conn):
    while True:
        try:
            # 发送屏幕图像
            img_data = capture_screen()
            data = pickle.dumps(img_data)
            conn.sendall(struct.pack("Q", len(data)) + data)
            
            # 接收输入事件
            input_data = conn.recv(1024)
            if not input_data:
                break
            event = pickle.loads(input_data)
            if event['type'] == 'mouse':
                pyautogui.moveTo(event['x'], event['y'])
            elif event['type'] == 'click':
                pyautogui.click()
            elif event['type'] == 'key':
                pyautogui.press(event['key'])
            time.sleep(0.05)  # 控制帧率
        except Exception as e:
            print(f"Error: {e}")
            break
    conn.close()

def start_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(1)
    print(f"Server listening on {HOST}:{PORT}")
    while True:
        conn, addr = s.accept()
        print(f"Connected by {addr}")
        threading.Thread(target=handle_client, args=(conn,)).start()

if __name__ == "__main__":
    start_server()
