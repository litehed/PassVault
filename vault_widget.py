from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton
from postgres_funcs import save_credential


class VaultWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add New Credential")
        self.setFixedSize(300, 200)

        layout = QVBoxLayout()

        self.app = QLineEdit()
        self.app.setPlaceholderText("App Name")
        layout.addWidget(self.app)

        self.user = QLineEdit()
        self.user.setPlaceholderText("Username")
        layout.addWidget(self.user)

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        layout.addWidget(self.password)

        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.handle_save)
        layout.addWidget(self.save_btn)

        self.setLayout(layout)

    def handle_save(self):
        name = self.app.text()
        user = self.user.text()
        pw = self.password.text()

        if name and user and pw:
            success = save_credential(name, user, pw)
            if success:
                print("✅ Saved successfully!")
                self.close()
            else:
                print("Hmmmmm, failed to save.")
        else:
            print("All fields must be filled. :()")
