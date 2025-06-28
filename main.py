from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QMainWindow, QDialog, QTreeWidget, QTreeWidgetItem, QLabel, QMenu, QMessageBox
from PySide6.QtGui import QIcon
from PySide6.QtCore import QTimer, Qt
from postgres_funcs import fetch_credentials, delete_credential
import sys
from vault_dialog import VaultDialog
from login_dialog import LoginDialog


class MainWindow(QMainWindow):
    def __init__(self, db_password):
        super().__init__()
        self.setWindowTitle("Password Manager")
        self.setWindowIcon(QIcon("VaultClosed.png"))
        self.setFixedSize(400, 300)

        self.db_password = db_password
        self.LOCK_TIMEOUT_SECONDS = 5 * 60
        self.remaining_time = self.LOCK_TIMEOUT_SECONDS

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
        self.tree_widget.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree_widget.customContextMenuRequested.connect(
            self.show_context_menu)
        layout.addWidget(self.tree_widget)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        app.installEventFilter(self)

        self.load_credentials()

    def show_context_menu(self, position):
        item = self.tree_widget.itemAt(position)
        if item is None:
            return

        top_level_item = item
        while top_level_item.parent() is not None:
            top_level_item = top_level_item.parent()

        context_menu = QMenu(self)

        edit_action = context_menu.addAction("Edit")
        delete_action = context_menu.addAction("Delete")
        copy_action = context_menu.addAction(f"Copy {item.text(0)}")

        action = context_menu.exec(self.tree_widget.mapToGlobal(position))

        if action == edit_action:
            self.edit_credential(top_level_item)
        elif action == delete_action:
            self.delete_credential(top_level_item)
        elif action == copy_action:
            self.copy_single_to_clipboard(item.text(1))

    def copy_single_to_clipboard(self, value):
        clipboard = QApplication.clipboard()
        clipboard.setText(value)

    def update_countdown(self):
        self.remaining_time -= 1
        if self.remaining_time <= 0:
            self.remaining_time = 0
        minutes = self.remaining_time // 60
        seconds = self.remaining_time % 60
        self.countdown_label.setText(
            f"Time until auto-lock: {minutes}:{seconds:02d}")

    def reset_inactivity_timer(self):
        self.remaining_time = self.LOCK_TIMEOUT_SECONDS
        self.inactivity_timer.start()

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
            self.remaining_time = self.LOCK_TIMEOUT_SECONDS
            self.countdown_timer.start()
            self.inactivity_timer.start()

    def open_add_popup(self):
        self.popup = VaultDialog(self.db_password)
        self.popup.show()
        self.popup.finished.connect(self.load_credentials)

    def load_credentials(self):
        self.tree_widget.clear()
        for service, user, password in fetch_credentials(self.db_password):
            parent = QTreeWidgetItem([service])
            child_user = QTreeWidgetItem(["Username", user])
            child_pass = QTreeWidgetItem(["Password", password])
            parent.addChildren([child_user, child_pass])
            self.tree_widget.addTopLevelItem(parent)

    def delete_credential(self, tree_item):
        app_name = tree_item.text(0)

        username = ""
        for i in range(tree_item.childCount()):
            child = tree_item.child(i)
            if child.text(0) == "Username":
                username = child.text(1)
                break

        reply = QMessageBox.question(
            self,
            'Confirm Deletion',
            f'Are you sure you want to delete the credential for "{app_name}" (user: {username})?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            success = delete_credential(app_name, username, self.db_password)
            if success:
                print(f"Deleted credential for {app_name}")
                self.load_credentials()
            else:
                QMessageBox.warning(
                    self, "Error", "Failed to delete credential")

    def edit_credential(self, tree_item):
        app_name = tree_item.text(0)

        username = ""
        password = ""
        for i in range(tree_item.childCount()):
            child = tree_item.child(i)
            if child.text(0) == "Username":
                username = child.text(1)
            elif child.text(0) == "Password":
                password = child.text(1)

        existing_data = {
            'app_name': app_name,
            'username': username,
            'password': password
        }

        self.popup = VaultDialog(
            self.db_password, edit_mode=True, existing_data=existing_data)
        self.popup.finished.connect(self.load_credentials)
        self.popup.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    login = LoginDialog()
    if login.exec() == QDialog.DialogCode.Accepted and login.authenticated:
        window = MainWindow(login.entered_password)
        window.show()
        app.exec()
        if isinstance(login.entered_password, bytearray):
            for i in range(len(login.entered_password)):
                login.entered_password[i] = 0
        sys.exit()
    else:
        sys.exit()
