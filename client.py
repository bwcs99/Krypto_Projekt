import socket
import ssl
from zp_group import ZpGroup
from schnorr_scheme import SchnorrScheme
from av_net import AVNet


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

        self.id = None
        self.product = None
        self.product_exponent = None
        self.av_private_key = None
        self.av_public_key = None

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

        # tu klient otrzymuje ustaloną grupę
        group_message = self.client_connection.recv(4096).decode('utf-8')
        g, p, q = (int(j) for j in iter(group_message.split(',')))
        game_group = ZpGroup(g, p, q)

        # tu generuje klucze i podpis
        signature_scheme = SchnorrScheme(game_group)
        private_key, public_key = signature_scheme.get_key()
        signature = signature_scheme.sign(private_key, public_key)
        self.av_private_key = private_key
        self.av_public_key = public_key

        # tu wysyła klucz wraz z podpisem
        u, c, z = signature
        signature_message = f"{public_key},{u},{c},{z}"
        self.client_connection.sendall(signature_message.encode('utf-8'))

        verification_status = int(self.client_connection.recv(4096).decode('utf-8'))
        if verification_status == 0:
            print("Verification failed.")
        else:
            id = int(self.client_connection.recv(4096).decode('utf-8'))
            self.id = id
            greeting = self.client_connection.recv(4096).decode('utf-8')
            print(f'{greeting}')

        initial_message_from_server = self.client_connection.recv(4096).decode('utf-8')

        if initial_message_from_server == f'NEP':
            print('Please wait for other participants to join...')

            _ = self.client_connection.recv(4096).decode('utf-8')

        print('We can start the game now...')

        # otrzymujemy od serwera klucze publiczne innych
        parsed_keys = self.client_connection.recv(4096).decode('utf-8')
        keys = [int(k) for k in parsed_keys.split(",")]
        av_service = AVNet(game_group)
        self.product, self.product_exponent = av_service.compute_product(self.id, keys)

        while True:
            time_message_from_server = self.client_connection.recv(4096).decode('utf-8')
            print(f'{time_message_from_server}')

            question_from_client = str(input(f'Type in your question: >'))

            self.client_connection.sendall(question_from_client.encode('utf-8'))

            answer_time_from_server = self.client_connection.recv(4096).decode('utf-8')

            print(f'Server: {answer_time_from_server}')

            question = self.client_connection.recv(4096).decode('utf-8')

            print(question)

            user_answer = int(input(f'Type in your answer (0/1):> ').strip())

            # w zależności od inputu obliczamy publiczną odpowiedź oraz generujemy ZKP dla wykładnika
            exponent, exponent_pub_key, public_exponent = av_service.generate_public_answer(self.product_exponent, user_answer,
                                                                                          self.av_private_key)

            """
            # na potrzeby testowania
            print(f"id:{self.id}")
            print(f"x: {self.av_private_key}")
            print(f"p,q:{game_group.p}, {game_group.q}")
            print(f"g: {game_group.group_generator}")
            print(f"g^x: {self.av_public_key}")
            print(f"c: {exponent}")
            print(f"cy: {public_exponent}")
            print(f"g^y:{self.product}")
            print(f"y: {self.product_exponent}")
            """
            u, c, z = signature_scheme.sign(exponent, exponent_pub_key)

            parsed_answer = f"{public_exponent},{exponent_pub_key},{u},{c},{z}"

            self.client_connection.sendall(parsed_answer.encode('utf-8'))

            verification_status = int(self.client_connection.recv(4096).decode('utf-8'))
            if verification_status == 0:
                print("Answer verification failed")
                break

            answers = self.client_connection.recv(4096).decode('utf-8')
            answers = [float(a) for a in answers.split(",")]

            group_answer = av_service.compute_group_answer(answers)

            print(f"group_answer:{group_answer}")

    """
    Funkcja (może zniknie) do wysyłania wiadomości do serwera
    """

    def send_message_to_server(self, message):
        self.client_connection.send(message.encode('utf-8'))

    """
    Funkcja (może zniknie) do odbierania wiadomości z serwera
    """

    def receive_message_from_sever(self):
        return self.client_connection.recv(4096).decode('utf-8')


# testy
if __name__ == "__main__":
    client = Client('192.168.0.15', 8083, 'BW CA Ltd', 'certificates/participant1.key',
                    'certificates/participant1.crt')

    client.connect_to_server()
