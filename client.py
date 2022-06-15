import socket
import ssl
import threading
from PyQt5.QtWidgets import QApplication
import sys
from PyQt5.QtCore import pyqtSignal, QObject


class Client(QObject):
    """
    Klasa klienta do komunikowania się z serwerem
    """

    display_message_from_server = pyqtSignal(str, str)

    def __init__(self, server_address, server_port, server_host_name, client_key_location, client_cert_location,
                 data_queue):

        super().__init__()

        self.server_address = server_address
        self.server_port = server_port
        self.server_host_name = server_host_name

        self.client_key_location = client_key_location
        self.client_cert_location = client_cert_location

        self.data_queue = data_queue

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

        self.display_message_from_server.emit(greeting, f'#0accee')

        initial_message_from_server = self.client_connection.recv(4096).decode('utf-8')

        if initial_message_from_server == f'NEP':
            self.display_message_from_server.emit('Please wait for other participants to join...', f'#000000')

            _ = self.client_connection.recv(4096).decode('utf-8')

        self.display_message_from_server.emit('We can start the game now...', f'#000000')

        while True:
            time_message_from_server = self.client_connection.recv(4096).decode('utf-8')

            self.display_message_from_server.emit(time_message_from_server, f'#0a11ee')

            question_from_client = self.data_queue.get()

            self.client_connection.sendall(question_from_client.encode())

            answer_time_from_server = self.client_connection.recv(4096).decode('utf-8')

            self.display_message_from_server.emit(f'Server: {answer_time_from_server}', f'#0a11ee')

            question = self.client_connection.recv(4096).decode('utf-8')

            self.display_message_from_server.emit(question, f'#0aee41')

            self.display_message_from_server.emit(f'Choose your answer (0/1)', f'#ee0a37')

            user_answer = str(self.data_queue.get())

            self.client_connection.sendall(user_answer.encode())

            group_answer_from_server = self.client_connection.recv(4096).decode('utf-8')

            self.display_message_from_server.emit(group_answer_from_server, f'#ee0a37')

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

    def append_to_data_queue(self, data):
        self.data_queue.put(data)


