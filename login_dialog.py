from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel
import psycopg2


class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enter Master Password")
        self.setFixedSize(300, 100)

        layout = QVBoxLayout()

        self.label = QLabel("Enter your master password:")
        layout.addWidget(self.label)

        self.password_input = QLineEdit()
        layout.addWidget(self.password_input)

        self.login_btn = QPushButton("Unlock")
        self.login_btn.clicked.connect(self.try_login)
        layout.addWidget(self.login_btn)

        self.setLayout(layout)
        self.authenticated = False
        self.entered_password = ""

    def try_login(self):
        pw = self.password_input.text()
        try:
            conn = psycopg2.connect(
                user="postgres",
                password=pw,
                host="localhost",
                port="5432",
                database="thevault"
            )
            self.authenticated = True
            self.entered_password = pw
            conn.close()
            self.accept()
        except Exception:
            self.label.setText("Incorrect password. Try again.")
            self.password_input.clear()
