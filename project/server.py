import socket
import json
from datetime import datetime
import threading

HOST = '0.0.0.0'
PORT = 5555


def handle_client(conn, addr):

    try:
        chunks = []

        while True:
            chunk = conn.recv(4096)
            if not chunk:
                break
            chunks.append(chunk)

        full_data = b"".join(chunks)

        if full_data:
            info = json.loads(full_data.decode('utf-8'))

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"\n--- Yangi Ulanish ({timestamp}) ---\n"
            log_entry += f"IP Manzil: {addr[0]}\n"
            log_entry += f"Saytlar: {info.get('websites', [])}\n"
            log_entry += f"Dasturlar: {info.get('processes', [])}\n"


            with open("mac_logs.txt", "a", encoding="utf-8") as log_file:
                log_file.write(log_entry)

            print(f"{addr[0]} data acceptd! ({len(full_data)} bayt)")

    except Exception as e:
        print(f"=error ({addr}): {e}")
    finally:
        conn.close()


def start_server():
    print(f"Server {HOST}:{PORT}running")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()

        while True:
            conn, addr = s.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.daemon = True
            thread.start()


if __name__ == "__main__":
    start_server()