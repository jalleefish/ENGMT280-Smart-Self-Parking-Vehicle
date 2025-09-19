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

    # Only process if distances array is valid
    if len(distances) == 5:
        if distances[1] < 20:
            conn.sendall(b"motorReverse\n")
            conn.sendall(b"servoMiddle\n")
            print("Too close to front, reversing")
        elif distances[3] < 20 or distances[4] < 20:
            conn.sendall(b"motorForward\n")
            conn.sendall(b"servoMiddle\n")
            print("Too close to left, moving forward")
        elif distances[0] < 20:
            conn.sendall(b"servoLeft\n")
            print("Too close to right, turning left")
        elif distances[2] < 20:
            conn.sendall(b"servoRight\n")
            print("Too close to back, turning right")

    time.sleep(0.1)
