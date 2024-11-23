import socket
import os
import threading

# Konfigurasi server
HOST = "127.0.0.1"
PORT = 2121
BASE_DIR = "files"  # Direktori penyimpanan file

# Membuat direktori penyimpanan jika belum ada
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

def handle_client(client_socket, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    while True:
        try:
            command = client_socket.recv(8192).decode().strip()
            if not command:
                break

            if command == "LIST":
                # Menampilkan daftar file yang ada di server
                files = "\n".join(os.listdir(BASE_DIR))
                client_socket.send(files.encode())

            elif command.startswith("UPLOAD"):
                _, filename = command.split(maxsplit=1)
                filepath = os.path.join(BASE_DIR, filename)

                # Konfirmasi siap menerima file
                client_socket.send("READY".encode())

                with open(filepath, "wb") as f:
                    while True:
                        data = client_socket.recv(8192)
                        if data == b"DONE":
                            break
                        f.write(data)
                client_socket.send(f"[SUCCESS] File {filename} uploaded.".encode())

            elif command.startswith("DOWNLOAD"):
                _, filename = command.split(maxsplit=1)
                filepath = os.path.join(BASE_DIR, filename)

                if os.path.exists(filepath):
                    # Konfirmasi bahwa file ada
                    client_socket.send("READY".encode())

                    with open(filepath, "rb") as f:
                        while data := f.read(8192):
                            client_socket.send(data)
                        client_socket.send(b"DONE")
                else:
                    print(f"[DEBUG] File not found: {filepath}")
                    client_socket.send("[ERROR] File not found.".encode())

            elif command.startswith("MKDIR"):
                _, dirname = command.split(maxsplit=1)
                dirpath = os.path.join(BASE_DIR, dirname)

                try:
                    os.makedirs(dirpath)
                    client_socket.send(f"[SUCCESS] Directory {dirname} created.".encode())
                except Exception as e:
                    client_socket.send(f"[ERROR] Could not create directory: {str(e)}".encode())

            elif command.startswith("RMDIR"):
                _, dirname = command.split(maxsplit=1)
                dirpath = os.path.join(BASE_DIR, dirname)

                try:
                    os.rmdir(dirpath)
                    client_socket.send(f"[SUCCESS] Directory {dirname} removed.".encode())
                except Exception as e:
                    client_socket.send(f"[ERROR] Could not remove directory: {str(e)}".encode())

            elif command == "QUIT":
                client_socket.send("[DISCONNECTED] Goodbye!".encode())
                break

            else:
                client_socket.send("[ERROR] Invalid command.".encode())

        except Exception as e:
            print(f"[ERROR] {str(e)}")
            break

    client_socket.close()
    print(f"[DISCONNECTED] {addr} disconnected.")

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"[STARTED] Server running on {HOST}:{PORT}")

    while True:
        client_socket, addr = server_socket.accept()
        thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        thread.start()

if __name__ == "__main__":
    start_server()
