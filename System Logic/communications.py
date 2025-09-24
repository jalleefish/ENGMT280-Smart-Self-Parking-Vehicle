import socket
import json
import time

HOST = "0.0.0.0"
PORT = 5000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)
print("Waiting for ESP32...")
conn, addr = server_socket.accept()
print(f"Connected by {addr}")

buffer = ""
distances = []

while True:
    data = conn.recv(1024).decode()
    if not data:
        break
    buffer += data

    while "\n" in buffer:
        line, buffer = buffer.split("\n", 1)
        try:
            distances = json.loads(line)
            print("Distances:", distances)
        except json.JSONDecodeError:
            print("Bad data:", line)
            
    conn.sendall(b"steering 123\n")
    print("Servo Right")

    time.sleep(0.1)
