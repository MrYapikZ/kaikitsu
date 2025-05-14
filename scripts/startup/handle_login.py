import sys
import json
import requests
from PyQt6.QtWidgets import QWidget, QMessageBox, QDialog
from ui.prelaunch.login import Ui_Form as LoginUI

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
            response, cookies = self.authenticate_user(email, password)

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

    def authenticate_user(self, email, password):
        """Make API request to authenticate user"""
        api_url = "http://expiproject.com/api/v1/launcher/auth/login"

        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        payload = {"username": email, "password": password}

        try:
            response = requests.post(api_url, headers=headers, json=payload)
            print(f"JSON: {response.json()}")
            return response.json(), response.cookies
        except requests.RequestException as e:
            return {"success": False, "message": f"Network error: {e}"}

    # def show_message(self, title, message):
    #     """Display a message box"""
    #     msg = QMessageBox(self)
    #     msg.setWindowTitle(title)
    #     msg.setText(message)
    #     msg.setIcon(QMessageBox.Icon.Warning if title == "Error" else QMessageBox.Icon.Information)
    #     msg.exec()
