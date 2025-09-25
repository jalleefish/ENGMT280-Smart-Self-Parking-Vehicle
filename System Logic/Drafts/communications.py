import socket
import json
import time
import Drafts.imageProcessing as imgProc

HOST = "0.0.0.0"
PORT = 5000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)
print("Waiting for ESP32...")
conn, addr = server_socket.accept()
print(f"Connected by {addr}")

buffer = ""

while True:
    data = conn.recv(1024).decode()
    if not data:
        break
    buffer += data

    while "\n" in buffer:
        line, buffer = buffer.split("\n", 1)
        line = line.strip()
        if not line:
            continue
        imgProc.sender = line
        
        if imgProc.target:
            conn.sendall("saveDistance".encode())

    time.sleep(0.1)
