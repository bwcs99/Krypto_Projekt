import socket
import ssl


class Client:
    """
    Klasa klienta do komunikowania się z serwerem
    """

    def __init__(self, server_address, server_port, server_host_name, client_key_location, client_cert_location):
        self.server_address = server_address
        self.server_port = server_port
        self.server_host_name = server_host_name

        self.client_key_location = client_key_location
        self.client_cert_location = client_cert_location

        self.context = None
        self.client_socket = None
        self.client_connection = None

    """
    Funkcja do tworzenia kontekstu (dokładnie to samo co w serwerze)
    """
    def create_context(self):
        self.context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile='certs/server.crt')
        self.context.load_cert_chain(certfile=self.client_cert_location, keyfile=self.client_key_location)

    """
    Funkcja do łączenia i komunikowania się z serwerem
    """
    def connect_to_server(self):
        self.create_context()

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.client_connection = self.context.wrap_socket(self.client_socket, server_side=False,
                                                          server_hostname=self.server_host_name)

        self.client_connection.connect((self.server_address, self.server_port))

        greeting = self.client_connection.recv(4096).decode('utf-8')

        print(f'{greeting}')

        while True:
            message_from_client = str(input(f'Your message: >'))

            self.client_connection.send(message_from_client.encode())

            response = self.client_connection.recv(4096).decode('utf-8')

            print(f'{response}')

    """
    Funkcja (może zniknie) do wysyłania wiadomości do serwera
    """
    def send_message_to_server(self, message):
        self.client_connection.send(message.encode())

    """
    Funkcja (może zniknie) do odbierania wiadomości z serwera
    """
    def receive_message_from_sever(self):
        return self.client_connection.recv(4096).decode('utf-8')

#testy
if __name__ == "__main__":
    client = Client('127.0.0.1', 8082, 'game.com', 'certs/client.key', 'certs/client.crt')

    client.connect_to_server()


