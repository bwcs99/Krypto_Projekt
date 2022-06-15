import socket
import ssl
import threading
import time
import random


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

        self.number_of_expected_participants = -1

        self.active_connections = []

        self.questions_queue = []

        self.users_answers = []

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

        if len(self.active_connections) != self.number_of_expected_participants:
            client_connection.sendall('NEP'.encode())

        while len(self.active_connections) != self.number_of_expected_participants:
            pass

        client_connection.send('EP'.encode())

        while True:
            question_from_client = client_connection.recv(4096).decode('utf-8')

        client_connection.close()

    """
    Funkcja uruchamiająca serwer i implementująca ustalony protokół
    """

    def serve(self):
        initial_message = 'Hello to game server !'.encode()

        self.number_of_expected_participants = int(input(f'Give number of participants: '))

        self.create_server_context()

        self.bind_socket = socket.socket()
        self.bind_socket.bind((self.listening_address, self.listening_port))

        self.bind_socket.listen(5)

        while len(self.active_connections) != self.number_of_expected_participants:
            print(f'Waiting for client !')

            new_connection, client_address = self.bind_socket.accept()

            print("Client connected: {}:{}".format(client_address[0], client_address[1]))

            new_connection = self.context.wrap_socket(new_connection, server_side=True)

            new_connection.send(initial_message)

            self.active_connections.append(new_connection)

            if len(self.active_connections) != self.number_of_expected_participants:
                new_connection.sendall('NEP'.encode())

        for conn in self.active_connections:
            conn.sendall(f'EP'.encode())

        while len(self.active_connections) > 0:

            for conn in self.active_connections:
                conn.sendall(f'You have 15 s to type in your questions...'.encode())

            time.sleep(15)

            for conn in self.active_connections:
                question_from_client = conn.recv(4096).decode('utf-8')

                self.questions_queue.append(question_from_client)

            print(f'questions from clients: {self.questions_queue}')

            randomly_selected_question_from_client = self.questions_queue[random.randint(0, len(self.questions_queue) - 1)]

            self.questions_queue.clear()

            for conn in self.active_connections:
                conn.sendall('You have 15 s to answer...'.encode())

                question_from_server = f'Question: {randomly_selected_question_from_client}'

                conn.sendall(question_from_server.encode())

            time.sleep(15)

            for conn in self.active_connections:
                connection_user_answer = int(conn.recv(4096).decode('utf-8'))

                self.users_answers.append(connection_user_answer)

            group_answer = 0

            if 1 in self.users_answers:
                group_answer = 1

            self.users_answers.clear()

            for conn in self.active_connections:
                conn.sendall(f'Group answer: {group_answer}'.encode())

            time.sleep(5)


# testy
if __name__ == "__main__":
    server = Server('127.0.0.1', 8082, 'certificates/server_key.key', 'certificates/server_cert.crt')
    print(f'Server is staring...')

    server.serve()
