import socket
import ssl
import threading


class Server:
    """
    Klasa serwera mogącego obsługiwać wielu klientów jednocześnie za pomocą połączenia TLS (wersja alpha)
    """
    def __init__(self, listening_address, listening_port, server_key_location, server_cert_location):
        self.listening_address = listening_address
        self.listening_port = listening_port

        self.context = None
        self.bind_socket = None

        self.server_key_location = server_key_location
        self.server_cert_location = server_cert_location

        self.active_connections = []

    """
    Funkcja do tworzenia kontekstu SSL - potrzebne jeśli chcemy mieć połączenie TLS
    """
    def create_server_context(self):
        self.context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        self.context.load_cert_chain(certfile=self.server_cert_location, keyfile=self.server_key_location)

    """
    Funkcja do obsługi klienta - robi "echo" tego co klient wysłał do serwera 
    """
    def handle_client(self, client_connection):
        initial_message = 'Hello to game server !'.encode()

        client_connection.send(initial_message)

        while True:
            message_from_client = client_connection.recv(4096).decode('utf-8')

            reply = 'Servers reply: Tomato !' + message_from_client

            if not message_from_client:
                break

            client_connection.sendall(reply.encode())

        client_connection.close()

    """
    Funkcja uruchamiająca serwer
    """
    def serve(self):
        self.create_server_context()

        self.bind_socket = socket.socket()
        self.bind_socket.bind((self.listening_address, self.listening_port))

        self.bind_socket.listen(5)

        while True:
            print(f'Waiting for client !')
            new_connection, client_address = self.bind_socket.accept()
            print("Client connected: {}:{}".format(client_address[0], client_address[1]))
            new_connection = self.context.wrap_socket(new_connection, server_side=True)
            print("SSL established. Peer: {}".format(new_connection.getpeercert()))

            client_thread = threading.Thread(target=self.handle_client, args=(new_connection,))

            client_thread.start()


# testy
if __name__ == "__main__":
    server = Server('127.0.0.1', 8082, 'certs/server.key', 'certs/server.crt')
    print(f'Server is staring...')

    server.serve()


