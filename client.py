import socket
import ssl
from PyQt5.QtCore import pyqtSignal, QObject
from zp_group import ZpGroup
from schnorr_scheme import SchnorrScheme
from av_net import AVNet
from string_resources import client_messages
from multiprocessing import Queue


class Client(QObject):
    """
    Klasa klienta do komunikowania się z serwerem
    """

    display_message = pyqtSignal(str, str)

    def __init__(self, server_address, server_port, server_host_name, client_key_location, client_cert_location):

        super().__init__()

        self.server_address = server_address
        self.server_port = server_port
        self.server_host_name = server_host_name

        self.client_key_location = client_key_location
        self.client_cert_location = client_cert_location

        self.context = None
        self.client_socket = None
        self.client_connection = None

        self.id = None
        self.product = None
        self.av_private_key = None
        self.av_public_key = None

        self.question_queue = Queue()
        self.answer_queue = Queue()

    """
    Funkcja do tworzenia kontekstu (dokładnie to samo co w serwerze)
    """

    def create_context(self):
        self.context = ssl.create_default_context()
        self.context.load_cert_chain(certfile=self.client_cert_location, keyfile=self.client_key_location)

    def get_group_from_server(self):
        group_message = self.client_connection.recv(4096).decode('utf-8')
        g, p, q = (int(j) for j in iter(group_message.split(',')))

        return ZpGroup(g, p, q)

    def publish_public_ephemeral_key(self, signature_scheme):
        private_key, public_key = signature_scheme.get_key()
        signature = signature_scheme.sign(private_key, public_key)
        self.av_private_key = private_key
        self.av_public_key = public_key

        u, c, z = signature
        signature_message = f"{public_key},{u},{c},{z}"
        self.client_connection.sendall(signature_message.encode('utf-8'))

        verification_status = int(self.client_connection.recv(4096).decode('utf-8'))
        if verification_status == 0:
            print(client_messages.verification_failure_message)
        else:
            id = int(self.client_connection.recv(4096).decode('utf-8'))
            self.id = id
            greeting = self.client_connection.recv(4096).decode('utf-8')

            self.display_message.emit(greeting, f'#0accee')

    def get_ephemeral_keys_from_another_users(self, game_group):
        parsed_keys = self.client_connection.recv(4096).decode('utf-8')
        keys = [int(k) for k in parsed_keys.split(",")]
        av_service = AVNet(game_group)
        self.product = av_service.compute_product(self.id, keys)

        return av_service

    def publish_answer(self, signature_scheme, exponent, exponent_pub_key, answer):
        u, c, z = signature_scheme.sign(exponent, exponent_pub_key)

        parsed_answer = f"{answer},{exponent_pub_key},{u},{c},{z}"

        self.client_connection.sendall(parsed_answer.encode('utf-8'))

        verification_status = int(self.client_connection.recv(4096).decode('utf-8'))
        if verification_status == 0:
            print(client_messages.answer_verification_failure_message)

    """
    Funkcja do łączenia, komunikowania się z serwerem i grania w grę według ustalonego protokołu
    """

    def connect_to_server(self):
        self.create_context()

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.client_connection = self.context.wrap_socket(self.client_socket, server_side=False,
                                                          server_hostname=self.server_host_name)

        self.client_connection.connect((self.server_address, self.server_port))

        game_group = self.get_group_from_server()
        signature_scheme = SchnorrScheme(game_group)

        self.publish_public_ephemeral_key(signature_scheme)

        initial_message_from_server = self.client_connection.recv(4096).decode('utf-8')

        if initial_message_from_server == f'NEP':
            self.display_message.emit(client_messages.wait_for_others_message, f'#000000')

            _ = self.client_connection.recv(4096).decode('utf-8')

        self.display_message.emit(client_messages.start_game_message, f'#000000')

        av_service = self.get_ephemeral_keys_from_another_users(game_group)

        while True:
            time_message_from_server = self.client_connection.recv(4096).decode('utf-8')

            self.display_message.emit(time_message_from_server, f'#0a11ee')

            question_from_client = self.question_queue.get()

            self.client_connection.sendall(question_from_client.encode('utf-8'))

            answer_time_from_server = self.client_connection.recv(4096).decode('utf-8')

            self.display_message.emit(f'Server: {answer_time_from_server}', f'#0a11ee')

            question = self.client_connection.recv(4096).decode('utf-8')

            self.display_message.emit(question, f'#0aee41')

            self.display_message.emit(client_messages.clients_answer_submit_message, f'#ee0a37')

            user_answer = int(self.answer_queue.get())

            exponent, answer, exponent_pub_key = av_service.generate_public_answer(self.product, user_answer,
                                                                                   self.av_private_key)

            self.publish_answer(signature_scheme, exponent, exponent_pub_key, answer)

            answers = self.client_connection.recv(4096).decode('utf-8')
            answers = [float(a) for a in answers.split(",")]

            group_answer = av_service.compute_group_answer(answers)

            self.display_message.emit(client_messages.group_answer_message + f'{group_answer}', f'#ee0a37')

    def append_to_questions_queue(self, users_question):
        self.question_queue.put(users_question)

    def append_to_answers_queue(self, users_answer):
        self.answer_queue.put(users_answer)
