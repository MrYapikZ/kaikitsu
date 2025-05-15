import sys
import json
import requests
from PyQt6.QtWidgets import QWidget, QMessageBox, QDialog
from ui.prelaunch.login_ui import Ui_Form as LoginUI
from scripts.main.request.api import RequestAPI

class LoginHandler(QDialog):  # <-- Use QDialog to make login a modal window
    def __init__(self):
        super().__init__()

        # Add cookies storage
        self.cookies = None

        # Load UI
        self.ui = LoginUI()
        self.ui.setupUi(self)

        # Connect login button
        self.ui.pushButtonLogIn.clicked.connect(self.handle_login)

    def get_cookies(self):
        """Returns the cookies if available"""
        return self.cookies

    def handle_login(self):
        """Handles user login"""
        email = self.ui.lineEditEmail.text().strip()
        password = self.ui.lineEditPassword.text()

        if not email or not password:
            # self.show_message("Error", "Please enter both email and password.")
            print("Error: Please enter both email and password.")
            return

        try:
            response, cookies = RequestAPI.authenticate_user(email, password)

            if response.get('success'):
                # self.show_message("Success", "Login successful!")
                self.cookies = cookies
                print("Success:", response.get('message', 'Login successful!'))
                self.accept()  # Close login window and return success
            else:
                # self.show_message("Error", response.get('message', 'Login failed. Please try again.'))
                print("Error:", response.get('message', 'Login failed. Please try again.'))

        except Exception as e:
            # self.show_message("Error", f"Connection error: {str(e)}")
            print("Error:", f"Connection error: {str(e)}")