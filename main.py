import sys
from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtGui import QPixmap, QIcon, QDesktopServices
from PyQt6.QtWidgets import QApplication, QMainWindow
from scripts.startup.handle_login import LoginHandler
from scripts.main.main_script import MainHandler
from scripts.main.request.api import RequestAPI
from ui.main.main_ui import Ui_MainWindow as MainWindowUI

class MainUI(QMainWindow, MainHandler):
    def __init__(self):
        super().__init__()

        # Instantiate and set up UI
        self.ui = MainWindowUI()
        self.ui.setupUi(self)

        # Cookies storage
        self.cookies = None

        if self.init():  # returns True on successful login
            self.main()
            self.show()  # Show main window only after login
        else:
            self.close()  # Close if login failed

    def init(self):
        # Show login window first
        login_handler = LoginHandler()

        if login_handler.exec():  # Wait for login to complete
            self.cookies = login_handler.get_cookies()
            return True
        return False

    def main(self):
        self.ui.pushButton_logOut.clicked.connect(self.handle_logout)
        self.ui.label_credit.mouseDoubleClickEvent = self.open_website

# PyQt Program =====================================================================================
    def open_website(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            QDesktopServices.openUrl(QUrl("https://www.expiproject.com/"))  # Open URL

    def handle_logout(self):
        # Logic for handling logout
        print("Logging out...")
        # RequestAPI.api_req_logout(self)
        self.cookies = None
        # Re-init login flow
        if not self.init():
            self.close()  # User cancelled login again

if __name__== "__main__":
    app = QApplication(sys.argv)
    ui = MainUI()
    ui.show()
    app.exec()