import socket
import threading

# Konfiguracja
HOST = '0.0.0.0'  # Słucha na wszystkich kartach sieciowych
PORT = 5000


def handle_receiving(conn):
    """Funkcja do działania w osobnym wątku - tylko odbiera dane"""
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                print("\n[Połączenie zakończone przez drugą stronę]")
                break
            print(f"\n[Odebrano]: {data.decode('utf-8')}")
            print("Twoja wiadomość: ", end="", flush=True)
        except ConnectionResetError:
            break
    conn.close()


def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        print(f"Serwer oczekuje na połączenie na porcie {PORT}...")

        conn, addr = s.accept()
        print(f"Połączono z: {addr}")

        # Uruchamiamy wątek do odbierania, żeby nie blokował wysyłania
        receiver_thread = threading.Thread(target=handle_receiving, args=(conn,), daemon=True)
        receiver_thread.start()

        # Główna pętla do wysyłania wiadomości z konsoli
        while True:
            msg = input("Twoja wiadomość: ")
            if msg.lower() == 'exit':
                break
            conn.sendall(msg.encode('utf-8'))


if __name__ == "__main__":
    start_server()