import socket
import ssl
import time
import random
from schnorr_scheme import SchnorrScheme
from zp_group import ZpGroup
from string_resources import server_messages


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
        self.timeout_for_question_writing = -1
        self.timeout_for_answering = -1

        self.active_connections = []

        self.questions_queue = []

        self.users_answers = []
        self.users_keys = []

    """
    Funkcja do tworzenia kontekstu SSL - potrzebne jeśli chcemy mieć połączenie TLS
    """

    def create_server_context(self):
        self.context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        self.context.load_cert_chain(certfile=self.server_cert_location, keyfile=self.server_key_location)

    def handle_and_verify_new_connection(self, new_connection, group_info, signature_scheme):
        group_message = ",".join([str(i) for i in iter(group_info)])
        new_connection.send(group_message.encode('utf-8'))

        signature_message = new_connection.recv(4096).decode('utf-8')
        public_key, u, c, z = (int(j) for j in iter(signature_message.split(',')))
        signature = (u, c, z)

        if signature_scheme.verify(public_key, signature) == 0:
            new_connection.send("0".encode('utf-8'))
        else:
            new_connection.send("1".encode('utf-8'))
            client_id = str(len(self.active_connections))
            new_connection.send(client_id.encode('utf-8'))
            new_connection.send(server_messages.server_initial_message.encode('utf-8'))
            self.active_connections.append(new_connection)
            self.users_keys.append(public_key)

        if len(self.active_connections) != self.number_of_expected_participants:
            new_connection.sendall(server_messages.not_enough_participants_flag.encode('utf-8'))

    def send_enough_participants_message(self):
        for conn in self.active_connections:
            conn.sendall(server_messages.enough_participants_flag.encode('utf-8'))
            keys_parsed = ",".join([str(k) for k in self.users_keys])
            conn.sendall(keys_parsed.encode('utf-8'))

    def get_questions_from_clients(self):
        for conn in self.active_connections:
            question_from_client = conn.recv(4096).decode('utf-8')

            self.questions_queue.append(question_from_client)

        selected_question_from_client = self.questions_queue[random.randint(0, len(self.questions_queue) - 1)]

        self.questions_queue.clear()

        return selected_question_from_client

    def send_selected_question_to_users(self, question):
        for conn in self.active_connections:
            conn.sendall(f'You have {self.timeout_for_answering} s to answer...'.encode('utf-8'))

            question_from_server = server_messages.server_question_message + f'{question}'

            conn.sendall(question_from_server.encode())

    def collect_answers_and_compute_result(self, signature_scheme):
        for conn in self.active_connections:

            answer = conn.recv(4096)
            answer = answer.decode('utf-8').split(',')
            user_answer = float(answer[0])
            exponent_pub_key = int(answer[1])
            u = int(answer[2])
            c = int(answer[3])
            z = int(answer[4])

            signature = (u, c, z)
            verification_result = signature_scheme.verify(exponent_pub_key, signature)

            if verification_result == 0:
                conn.send("0".encode())
            else:
                conn.send("1".encode())
                self.users_answers.append(user_answer)

        parsed_answers = ','.join([str(a) for a in self.users_answers])
        for conn in self.active_connections:
            conn.sendall(parsed_answers.encode('utf-8'))
        self.users_answers = []

    """
    Funkcja uruchamiająca serwer i implementująca ustalony protokół
    """

    def serve(self, nq):
        game_group = ZpGroup()
        game_group.generate_zp_group(nq)
        group_info = (game_group.get_zp_group_generator(), *game_group.get_primes())

        signature_scheme = SchnorrScheme(game_group)

        self.number_of_expected_participants = int(input(server_messages.number_of_participants_message))
        self.timeout_for_question_writing = int(input(server_messages.timeout_for_question_writing_message))
        self.timeout_for_answering = int(input(server_messages.timeout_for_answering_message))

        self.create_server_context()

        self.bind_socket = socket.socket()
        self.bind_socket.bind((self.listening_address, self.listening_port))

        self.bind_socket.listen(5)

        while len(self.active_connections) != self.number_of_expected_participants:
            print(server_messages.server_waiting_for_client_message)

            new_connection, client_address = self.bind_socket.accept()

            print(server_messages.connected_client_info_message.format(client_address[0], client_address[1]))

            new_connection = self.context.wrap_socket(new_connection, server_side=True)

            self.handle_and_verify_new_connection(new_connection, group_info, signature_scheme)

        self.send_enough_participants_message()

        while len(self.active_connections) > 0:

            for conn in self.active_connections:
                conn.sendall(f'You have {self.timeout_for_question_writing} s to type in your questions...'.encode())

            time.sleep(self.timeout_for_question_writing)

            randomly_selected_question_from_client = self.get_questions_from_clients()

            self.send_selected_question_to_users(randomly_selected_question_from_client)

            time.sleep(self.timeout_for_answering)

            self.collect_answers_and_compute_result(signature_scheme)

            time.sleep(5)


if __name__ == "__main__":
    server = Server('192.168.43.105', 8087, 'certificates/server_key.key', 'certificates/server_cert.crt')
    print(f'Server is staring...')

    server.serve(4)

