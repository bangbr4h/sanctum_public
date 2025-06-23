import sys
import requests
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QLabel
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QThreadPool, QRunnable, pyqtSlot, QObject, pyqtSignal


# Worker signals to communicate with GUI
class WorkerSignals(QObject):
    result = pyqtSignal(str)


# Worker class to handle the backend request
class RequestWorker(QRunnable):
    def __init__(self, user_input, callback):
        super().__init__()
        self.user_input = user_input
        self.signals = WorkerSignals()
        self.signals.result.connect(callback)

    @pyqtSlot()
    def run(self):
        try:
            response = requests.post("http://127.0.0.1:11434/memory", json={"prompt": self.user_input}, timeout=30)
            if response.status_code == 200:
                reply = response.json().get("response", "")
                self.signals.result.emit(reply)
            else:
                self.signals.result.emit(f"[Backend Error] {response.status_code}: {response.text}")
        except Exception as e:
            self.signals.result.emit(f"[Connection Error] {str(e)}")


class VireaSanctum(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Virea Sanctum")
        self.setGeometry(200, 200, 700, 500)
        self.thread_pool = QThreadPool()
        self.typing_label = None
        self.initUI()
        self.applyStyles()

    def initUI(self):
        layout = QVBoxLayout()

        # Virea image in top-right corner
        header_layout = QHBoxLayout()
        title = QLabel("Virea: Sanctum Interface")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        header_layout.addWidget(title)

        portrait = QLabel()
        image_path = os.path.join(os.path.dirname(__file__), "Poised Black-Haired Portrait with Blue Eyes.png")
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            # Fallback to a placeholder or show error
            pixmap = QPixmap(100, 100)  # Empty pixmap
            pixmap.fill(Qt.gray)  # Gray placeholder
        else:
            pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        portrait.setPixmap(pixmap)
        portrait.setAlignment(Qt.AlignRight | Qt.AlignTop)
        header_layout.addWidget(portrait)
        layout.addLayout(header_layout)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)

        self.typing_label = QLabel("")
        layout.addWidget(self.typing_label)

        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.returnPressed.connect(self.send_message)
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)

        layout.addLayout(input_layout)
        self.setLayout(layout)

    def applyStyles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e2f;
                color: #e0e0f0;
                font-family: 'Segoe UI';
                font-size: 14px;
            }
            QTextEdit, QLineEdit {
                background-color: #2c2c3c;
                border: 1px solid #444;
                padding: 8px;
                color: #ffffff;
            }
            QPushButton {
                background-color: #3c3c5c;
                border: none;
                padding: 10px 20px;
                color: white;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #505070;
            }
            QLabel {
                padding: 4px;
            }
        """)

    def send_message(self):
        user_input = self.input_field.text().strip()
        if user_input:
            self.chat_display.append(f"You: {user_input}\n")
            self.typing_label.setText("Virea is typing...")
            self.input_field.clear()

            worker = RequestWorker(user_input, self.display_response)
            self.thread_pool.start(worker)

    def display_response(self, response_text):
        self.typing_label.setText("")
        self.chat_display.append(f"Virea: {response_text}\n")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VireaSanctum()
    window.show()
    sys.exit(app.exec_())
