from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton
from postgres_funcs import save_credential, update_credential


class VaultDialog(QDialog):
    def __init__(self, db_password, edit_mode=False, existing_data=None):
        super().__init__()

        self.db_password = db_password
        self.edit_mode = edit_mode
        self.existing_data = existing_data or {}

        if edit_mode:
            self.setWindowTitle("Edit Credential")
        else:
            self.setWindowTitle("Add New Credential")

        self.setFixedSize(300, 220)

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

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        layout.addWidget(self.cancel_btn)
        
        if edit_mode and existing_data:
            self.app.setText(existing_data.get('app_name', ''))
            self.user.setText(existing_data.get('username', ''))
            self.password.setText(existing_data.get('password', ''))

        self.setLayout(layout)

    def handle_save(self):
        name = self.app.text().strip()
        user = self.user.text().strip()
        pw = self.password.text()

        if not name or not user or not pw:
            print("All fields must be filled. :()")
            return

        success = False

        if self.edit_mode:
            old_app_name = self.existing_data.get('app_name', '')
            old_username = self.existing_data.get('username', '')
            success = update_credential(old_app_name, old_username, name, user, pw, self.db_password)
        else:
            success = save_credential(name, user, pw, self.db_password)

        if success:
            action = "Updated" if self.edit_mode else "Saved"
            print(f"{action} successfully!")
            self.accept()
        else:
            action = "update" if self.edit_mode else "save"
            print(f"Failed to {action} credential.")
