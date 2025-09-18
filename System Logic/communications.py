import socket

# Choose the same port as in your ESP32 sketch
HOST = "0.0.0.0"   # listen on all interfaces
PORT = 5000        # <-- make sure this matches 'port' in Communications.cpp

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen(1)
        print(f"Server listening on {HOST}:{PORT}")

        while True:
            conn, addr = server_socket.accept()
            with conn:
                print(f"Connected by {addr}")
                while True:
                    data = conn.recv(1024)  # read up to 1024 bytes
                    if not data:
                        break
                    print("Received:", data.decode("utf-8"))
                    
                    

if __name__ == "__main__":
    start_server()
