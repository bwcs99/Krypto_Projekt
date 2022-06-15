from PyQt5.QtCore import Qt, QThread
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QTextEdit, QLabel, QHBoxLayout, QComboBox
import sys
from client import Client
from multiprocessing import Queue


class GameWindow(QWidget):

    def __init__(self, client_object):
        super().__init__()

        self.client_object = client_object

        window_layout = QVBoxLayout()

        question_place_layout = QHBoxLayout()

        question_label = QLabel(f'Question: ')

        self.question_field = QTextEdit()

        question_place_layout.addWidget(question_label)
        question_place_layout.addWidget(self.question_field)

        self.possible_answers = [f'0', f'1']

        answer_label = QLabel(f'Your answer: ')

        possible_answers_list = QComboBox()

        possible_answers_list.addItems(self.possible_answers)

        possible_answers_list.setMaximumWidth(80)

        possible_answers_list.activated.connect(lambda x: self.serve_submit_answer_request(x))

        self.question_field.setFixedWidth(500)
        self.question_field.setFixedHeight(30)

        self.server_messages_field = QTextEdit()
        self.server_messages_field.setReadOnly(True)

        self.submit_button = QPushButton(f'Submit')
        self.submit_button.clicked.connect(self.serve_submit_question_request)

        self.submit_button.setFixedWidth(100)
        self.submit_button.setFixedHeight(30)

        window_layout.addLayout(question_place_layout)

        window_layout.addWidget(self.submit_button)
        window_layout.setAlignment(self.submit_button, Qt.AlignCenter)

        window_layout.addSpacing(10)

        window_layout.addWidget(answer_label)
        window_layout.addWidget(possible_answers_list)

        window_layout.addSpacing(10)

        server_messages_label = QLabel(f'Messages from server: ')
        window_layout.addWidget(server_messages_label)

        window_layout.addWidget(self.server_messages_field)

        self.setLayout(window_layout)

        self.setWindowTitle(f'Social Game')
        self.setWindowIcon(QIcon(f'icons/game_icon.png'))
        self.setFixedSize(600, 600)

    def serve_submit_question_request(self):
        question_from_user = self.question_field.toPlainText()
        self.client_object.append_to_data_queue(question_from_user)

    def serve_submit_answer_request(self, idx):
        user_answer = int(self.possible_answers[idx])
        self.client_object.append_to_data_queue(user_answer)

    def display_message_from_server(self, message_from_server, text_color_hex):
        self.server_messages_field.setTextColor(QColor(text_color_hex))
        self.server_messages_field.append(f'> {message_from_server}')
        self.update()


# testy
if __name__ == "__main__":
    app = QApplication(sys.argv)

    data_queue = Queue()

    client = Client('127.0.01', 8082, 'BW CA Ltd', 'certificates/participant1.key',
                    'certificates/participant1.crt', data_queue)

    client_window = GameWindow(client)

    client_thread = QThread()

    client.moveToThread(client_thread)

    client_thread.started.connect(client.connect_to_server)
    client.display_message_from_server.connect(client_window.display_message_from_server)

    client_thread.start()

    client_window.show()

    sys.exit(app.exec())
