from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QMainWindow, QDialog, QTreeWidget, QTreeWidgetItem
from postgres_funcs import fetch_credentials
import sys
from vault_widget import VaultWidget
from login_dialog import LoginDialog


class MainWindow(QMainWindow):
    def __init__(self, password):
        super().__init__()
        self.setWindowTitle("Password Manager")
        self.setFixedSize(400, 300)

        self.password = password

        central_widget = QWidget()
        layout = QVBoxLayout()

        self.add_btn = QPushButton("Add New Credential")
        self.add_btn.clicked.connect(self.open_add_popup)
        layout.addWidget(self.add_btn)

        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["App", "Credentials"])
        layout.addWidget(self.tree_widget)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.load_credentials()

    def open_add_popup(self):
        self.popup = VaultWidget(self.password)
        self.popup.show()

    def load_credentials(self):
        self.tree_widget.clear()
        for service, user, password in fetch_credentials(self.password):
            parent = QTreeWidgetItem([service])
            child_user = QTreeWidgetItem(["Username", user])
            child_pass = QTreeWidgetItem(["Password", password])
            parent.addChildren([child_user, child_pass])
            self.tree_widget.addTopLevelItem(parent)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    login = LoginDialog()
    if login.exec() == QDialog.DialogCode.Accepted and login.authenticated:
        window = MainWindow(login.entered_password)
        window.show()
        sys.exit(app.exec())
    else:
        sys.exit()
