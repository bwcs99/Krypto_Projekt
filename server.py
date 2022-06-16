import socket
import ssl
import time
import random
from schnorr_scheme import SchnorrScheme
from zp_group import ZpGroup


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
        self.users_keys = []

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
            client_connection.sendall('NEP'.encode('utf-8'))

        while len(self.active_connections) != self.number_of_expected_participants:
            pass

        client_connection.send('EP'.encode('utf-8'))

        while True:
            question_from_client = client_connection.recv(4096).decode('utf-8')

        client_connection.close()

    """
    Funkcja uruchamiająca serwer i implementująca ustalony protokół
    """

    def serve(self, nq):
        initial_message = 'Hello to game server !'.encode('utf-8')

        # ustalenie grupy
        game_group = ZpGroup()
        game_group.generate_zp_group(nq)
        group_info = (game_group.get_zp_group_generator(), *game_group.get_primes())

        # podpis
        signature_scheme = SchnorrScheme(game_group)

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

            # tu powinniśmy wysłać klientowi (g,p,q)
            group_message = ",".join([str(i) for i in iter(group_info)])
            new_connection.send(group_message.encode('utf-8'))

            # tu otrzymujemy z powrotem pare klucz, podpis
            signature_message = new_connection.recv(4096).decode('utf-8')
            public_key, u, c, z = (int(j) for j in iter(signature_message.split(',')))
            signature = (u, c, z)

            # weryfikujemy podpis
            if signature_scheme.verify(public_key, signature) == 0:
                # jeśli weryfikacja się nie powiodła wysyłamy 0
                new_connection.send("0".encode('utf-8'))
            else:
                # jeśli się powiodła, nadajemy id, wysyłamy id, wysylamy powitanie, dodajemy połączenie do połączeń
                # klucz dodajemy do kluczy
                new_connection.send("1".encode('utf-8'))
                client_id = str(len(self.active_connections))
                new_connection.send(client_id.encode('utf-8'))
                new_connection.send(initial_message)
                self.active_connections.append(new_connection)
                self.users_keys.append(public_key)

            if len(self.active_connections) != self.number_of_expected_participants:
                new_connection.sendall('NEP'.encode('utf-8'))

        for conn in self.active_connections:
            # każdemu graczowi wysyłamy listę kluczy publicznych pozostałych graczy
            conn.sendall(f'EP'.encode('utf-8'))
            keys_parsed = ",".join([str(k) for k in self.users_keys])
            conn.sendall(keys_parsed.encode('utf-8'))

        while len(self.active_connections) > 0:

            for conn in self.active_connections:
                conn.sendall(f'You have 15 s to type in your questions...'.encode())

            time.sleep(15)

            for conn in self.active_connections:
                question_from_client = conn.recv(4096).decode('utf-8')

                self.questions_queue.append(question_from_client)

            print(f'questions from clients: {self.questions_queue}')

            randomly_selected_question_from_client = self.questions_queue[
                random.randint(0, len(self.questions_queue) - 1)]

            self.questions_queue.clear()

            for conn in self.active_connections:
                conn.sendall('You have 15 s to answer...'.encode())

                question_from_server = f'Question: {randomly_selected_question_from_client}'

                conn.sendall(question_from_server.encode())

            time.sleep(15)

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

                # serwer weryfikuje każdą wiadomość, jeśli jest okej dodaje do tablicy odpowiedzi

                if verification_result == 0:
                    conn.send("0".encode())
                else:
                    conn.send("1".encode())
                    self.users_answers.append(user_answer)

            parsed_answers = ','.join([str(a) for a in self.users_answers])
            for conn in self.active_connections:
                conn.sendall(parsed_answers.encode('utf-8'))
            self.users_answers = []

            time.sleep(5)


# testy
if __name__ == "__main__":
    server = Server('192.168.0.15', 8083, 'certificates/server_key.key', 'certificates/server_cert.crt')
    print(f'Server is staring...')

    server.serve(4)

