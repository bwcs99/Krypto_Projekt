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
        self.context = ssl.create_default_context()
        self.context.load_cert_chain(certfile=self.client_cert_location, keyfile=self.client_key_location)

    """
    Funkcja do łączenia, komunikowania się z serwerem i grania w grę według ustalonego protokołu
    """
    def connect_to_server(self):
        self.create_context()

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.client_connection = self.context.wrap_socket(self.client_socket, server_side=False,
                                                          server_hostname=self.server_host_name)

        self.client_connection.connect((self.server_address, self.server_port))

        greeting = self.client_connection.recv(4096).decode('utf-8')

        print(f'{greeting}')

        initial_message_from_server = self.client_connection.recv(4096).decode('utf-8')

        if initial_message_from_server == f'NEP':
            print('Please wait for other participants to join...')

            _ = self.client_connection.recv(4096).decode('utf-8')

        print('We can start the game now...')

        while True:
            time_message_from_server = self.client_connection.recv(4096).decode('utf-8')
            print(f'{time_message_from_server}')

            question_from_client = str(input(f'Type in your question: >'))

            self.client_connection.sendall(question_from_client.encode())

            answer_time_from_server = self.client_connection.recv(4096).decode('utf-8')

            print(f'Server: {answer_time_from_server}')

            question = self.client_connection.recv(4096).decode('utf-8')

            print(question)

            user_answer = input(f'Type in your answer (0/1):> ')

            self.client_connection.sendall(user_answer.encode())

            group_answer_from_server = self.client_connection.recv(4096).decode('utf-8')

            print(group_answer_from_server)

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
    client = Client('127.0.0.1', 8082, 'BW CA Ltd', 'certificates/participant1.key',
                    'certificates/participant1.crt')

    client.connect_to_server()


