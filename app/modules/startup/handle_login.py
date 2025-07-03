from PyQt6.QtWidgets import QDialog, QMessageBox

from app.config import Settings
from app.ui.startup.login_ui import Ui_Form as LoginUI
from app.services.auth import AuthServices
from app.core.app_states import AppState

class LoginHandler(QDialog):  # <-- Use QDialog to make login a modal window
    def __init__(self):
        super().__init__()

        # User data
        self.username = None

        # Load UI
        self.ui = LoginUI()
        self.ui.setupUi(self)
        self.ui.labelTitle.setText(Settings.APP_NAME)

        # Connect login button
        self.ui.pushButtonLogIn.clicked.connect(self.handle_login)

    def show_message(self, title: str, message: str, icon: QMessageBox.Icon = QMessageBox.Icon.Information):
        msg_box = QMessageBox(self)
        msg_box.setIcon(icon)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec()

    def handle_login(self):
        """Handles user login"""
        username = self.ui.lineEditEmail.text().strip()
        password = self.ui.lineEditPassword.text()
        kiyokai_url = self.ui.lineEditKiyokai.text()

        if not username or not password or not kiyokai_url:
            # self.show_message("Error", "Please enter both email and password.")
            print("[-] Error: Please enter kiyokai url, username and password.")
            self.show_message("Input Error", "Please enter all required fields.", QMessageBox.Icon.Warning)
            return

        AppState().set_kiyokai_url(kiyokai_url=kiyokai_url)

        if AppState().zou_url is None:
            # self.show_message("Error", "Invalid Kiyokai URL. Please check the URL and try again.")
            print("[-] Error: Invalid Kiyokai URL. Please check the URL and try again.")
            self.show_message("Kiyokai URL Error", "Zou URL not found. Please check the URL and try again.", QMessageBox.Icon.Warning)
            return

        try:
            response = AuthServices.authenticate_user(username, password)

            if response.get('success'):
                # self.show_message("Success", "Login successful!")
                user_data = response.get("user", {})
                self.username = user_data.get("full_name") or user_data.get("name") or username

                # Store Data
                AppState().set_access_token(response.get("access_token"))
                AppState().set_user_data(user_data)

                # Response
                print("[+] Success:", response.get('message', '[+] Login successful!'))
                self.show_message("Login Success", f"Welcome, {self.username}!", QMessageBox.Icon.Information)
                self.accept()  # Close login window and return success
            else:
                # self.show_message("Error", response.get('message', 'Login failed. Please try again.'))
                print("[-] Error:", response.get('message', '[-] Login failed. Please try again.'))
                self.show_message("Login Failed", response.get("message", "Login failed."), QMessageBox.Icon.Critical)


        except Exception as e:
            # self.show_message("Error", f"Connection error: {str(e)}")
            print("[-] Error:", f"[-] Connection error: {str(e)}")
            self.show_message("Connection Error", str(e), QMessageBox.Icon.Critical)