from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QTextEdit, QLabel, QHBoxLayout, QComboBox
from string_resources import client_messages


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

        self.possible_answers = [f'No', f'Yes']

        answer_label = QLabel(f'Your answer: ')

        possible_answers_list = QComboBox()

        possible_answers_list.addItems(self.possible_answers)

        possible_answers_list.setMaximumWidth(80)

        possible_answers_list.activated.connect(lambda x: self.serve_submit_answer_request(x))

        self.question_field.setFixedWidth(500)
        self.question_field.setFixedHeight(30)

        self.messages_field = QTextEdit()
        self.messages_field.setReadOnly(True)

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

        messages_label = QLabel(f'Messages: ')
        window_layout.addWidget(messages_label)

        window_layout.addWidget(self.messages_field)

        self.setLayout(window_layout)

        self.setWindowTitle(f'Social Game')
        self.setWindowIcon(QIcon(f'icons/game_icon.png'))
        self.setFixedSize(600, 600)

    def serve_submit_question_request(self):
        question_from_user = self.question_field.toPlainText()
        self.client_object.append_to_questions_queue(question_from_user)

        self.display_message(client_messages.question_submission_message, f'#ee0a9b')

    def serve_submit_answer_request(self, idx):
        if idx == 0:
            user_answer = 0
        else:
            user_answer = 1

        self.client_object.append_to_answers_queue(user_answer)

        self.display_message(client_messages.answer_submission_message, f'#ee0a9b')

    def display_message(self, message, text_color_hex):
        self.messages_field.setTextColor(QColor(text_color_hex))
        self.messages_field.append(f'> {message}')
        self.update()
