from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QMainWindow, QDialog, QTreeWidget, QTreeWidgetItem, QLabel
from PySide6.QtCore import QTimer, Qt
from postgres_funcs import fetch_credentials
import sys
from vault_widget import VaultWidget
from login_dialog import LoginDialog


class MainWindow(QMainWindow):
    def __init__(self, db_password):
        super().__init__()
        self.setWindowTitle("Password Manager")
        self.setFixedSize(400, 300)

        self.db_password = db_password
        self.remaining_time = 5 * 60

        self.inactivity_timer = QTimer(self)
        self.inactivity_timer.setInterval(self.remaining_time * 1000)
        self.inactivity_timer.timeout.connect(self.lock_vault)
        self.inactivity_timer.start()

        central_widget = QWidget()
        layout = QVBoxLayout()

        self.add_btn = QPushButton("Add New Credential")
        self.add_btn.clicked.connect(self.open_add_popup)
        layout.addWidget(self.add_btn)

        self.countdown_label = QLabel("Time until auto-lock: 5:00")
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.countdown_label)

        self.countdown_timer = QTimer(self)
        self.countdown_timer.setInterval(1000)  # 1 second
        self.countdown_timer.timeout.connect(self.update_countdown)
        self.countdown_timer.start()

        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["App", "Credentials"])
        layout.addWidget(self.tree_widget)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        app.installEventFilter(self)

        self.load_credentials()

    def update_countdown(self):
        self.remaining_time -= 1
        if self.remaining_time <= 0:
            self.remaining_time = 0
        minutes = self.remaining_time // 60
        seconds = self.remaining_time % 60
        self.countdown_label.setText(
            f"Time until auto-lock: {minutes}:{seconds:02d}")

    def reset_inactivity_timer(self):
        self.remaining_time = 5 * 60
        self.inactivity_timer.start()
        print("Inactivity timer reset.")

    def eventFilter(self, watched, event):
        if event.type() in (event.Type.KeyPress, event.Type.MouseButtonPress) and self.isEnabled():
            self.reset_inactivity_timer()
        return super().eventFilter(watched, event)

    def lock_vault(self):
        self.setDisabled(True)
        login = LoginDialog()
        if login.exec() == QDialog.DialogCode.Accepted and login.authenticated:
            self.db_password = login.entered_password
            self.load_credentials()
            self.setEnabled(True)
            self.remaining_time = 5 * 60
            self.countdown_timer.start()
            self.inactivity_timer.start()

    def open_add_popup(self):
        self.popup = VaultWidget(self.db_password)
        self.popup.show()

    def load_credentials(self):
        self.tree_widget.clear()
        for service, user, password in fetch_credentials(self.db_password):
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
