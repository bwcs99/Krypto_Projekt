import sys
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QApplication
from client import Client
from game_window import GameWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)

    client = Client('127.0.0.1', 8096, 'BW CA Ltd', 'certificates/participant1.key',
                    'certificates/participant1.crt')

    client_window = GameWindow(client)

    client_thread = QThread()

    client.moveToThread(client_thread)

    client_thread.started.connect(client.connect_to_server)
    client.display_message.connect(client_window.display_message)

    client_thread.start()

    client_window.show()

    sys.exit(app.exec())
