import os
import sys
import requests
from io import BytesIO
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QPixmap, QDesktopServices
from PyQt6.QtWidgets import QApplication, QMainWindow, QTreeWidgetItem, QListWidgetItem

from app.config import Settings
from app.modules.startup.handle_login import LoginHandler
from app.modules.main.handle_dashboard import DashboardHandler
from app.services.auth import AuthServices
from app.services.task import TaskService
from app.ui.main.main_ui import Ui_MainWindow as MainWindowUI
from app.core.app_states import AppState

class MainUI(QMainWindow):
    def __init__(self):
        super().__init__()

        # Instantiate and set up UI
        self.ui = MainWindowUI()
        self.ui.setupUi(self)

        if self.prelaunch():  # returns True on successful login
            self.load_ui()
            self.show()  # Show main window only after login
        else:
            self.close()  # Close if login failed

    def prelaunch(self):
        # Show login window first
        login_handler = LoginHandler()

        if login_handler.exec():  # Wait for login to complete
            return True
        return False

    def load_ui(self):
        # Load main UI components
        self.ui.label_programName.setText(Settings.APP_NAME)
        self.ui.pushButton_logOut.clicked.connect(self.handle_logout)
        self.ui.label_credit.mouseDoubleClickEvent = self.open_website
        self.ui.label_credit.setText(f"© {Settings.APP_NAME} - ExpiProject")
        self.ui.label_buildVersion.setText(f"Build: {Settings.BUILD_VERSION}")
        self.ui.label_username.setText(AppState().user_data["user"]["full_name"] or AppState().user_data["user"]["email"])
        if AppState().user_data["user"]["has_avatar"] and os.path.exists(Settings.AVATAR_FILE):
            self.load_avatar_image(f"{Settings.AVATAR_FILE}")

        # Set up tabs
        self.ui.tabWidget.addTab(DashboardHandler(), "Dashboard")

        TaskService().get_task_list()

# PyQt Program =====================================================================================
    def open_website(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            QDesktopServices.openUrl(QUrl("https://www.expiproject.com/"))  # Open URL

    def handle_logout(self):
        # Logic for handling logout
        print("Logging out...")
        AuthServices.api_req_logout()

        # Re-init login flow
        if not self.prelaunch():
            self.close()  # User cancelled login again

    def load_avatar_image(self, file_path):
        # Load image directly from local file path
        pixmap = QPixmap(file_path)
        if not pixmap.isNull():  # Check if image loaded successfully
            scaled_pixmap = pixmap.scaled(25, 25, Qt.AspectRatioMode.KeepAspectRatio,
                                          Qt.TransformationMode.SmoothTransformation)
            self.ui.label_userimage.setPixmap(scaled_pixmap)
            self.ui.label_userimage.setFixedSize(25, 25)
            self.ui.label_userimage.setScaledContents(True)
        else:
            print(f"Failed to load avatar image from: {file_path}")

if __name__== "__main__":
    app = QApplication(sys.argv)
    ui = MainUI()
    ui.show()
    app.exec()