import sys
import requests
from io import BytesIO
from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtGui import QPixmap, QIcon, QDesktopServices
from PyQt6.QtWidgets import QApplication, QMainWindow, QTreeWidgetItem
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest
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
        self.username = None
        self.avatarUrl = ""

        # Quick Scan storage
        self.projects_names = []
        self.episode_names = []
        self.sequence_names = []
        self.shot_names = []
        self.work_type_names = ["Assets", "Animation", "Lighting", "Modeling", "Compositing"]

        if self.prelaunch():  # returns True on successful login
            self.main()
            self.show()  # Show main window only after login
        else:
            self.close()  # Close if login failed

    def prelaunch(self):
        # Show login window first
        login_handler = LoginHandler()

        if login_handler.exec():  # Wait for login to complete
            self.cookies = login_handler.get_cookies()
            self.username, self.avatarUrl = login_handler.get_userdata()
            return True
        return False

    def main(self):

        self.ui.label_username.setText(self.username)
        self.load_avatar_image(self.avatarUrl)
        print(self.avatarUrl)

        self.ui.pushButton_logOut.clicked.connect(self.handle_logout)
        self.ui.label_credit.mouseDoubleClickEvent = self.open_website

        self.handle_quickscan()
        self.menu_quickSearch()

        self.menu_treeview()

# UI Program ======================================================================================
    def menu_quickSearch(self):
        self.ui.comboBox_project.clear()
        self.ui.comboBox_workType.clear()
        self.ui.comboBox_episode.clear()
        self.ui.comboBox_sequence.clear()
        self.ui.comboBox_shot.clear()

        self.ui.comboBox_project.addItem("Select Project")
        for name in self.projects_names:
            self.ui.comboBox_project.addItem(name)

        self.ui.comboBox_workType.addItem("Select Work Type")
        for name in self.work_type_names:
            self.ui.comboBox_workType.addItem(name)

        self.ui.comboBox_episode.addItem("Select Episode")
        for name in self.episode_names:
            self.ui.comboBox_episode.addItem(name)

        self.ui.comboBox_sequence.addItem("Select Sequence")
        for name in self.sequence_names:
            self.ui.comboBox_sequence.addItem(name)

        self.ui.comboBox_shot.addItem("Select Shot")
        for name in self.shot_names:
            self.ui.comboBox_shot.addItem(name)

        self.ui.pushButton_qucikScan.clicked.connect(self.handle_quickscan)

    def menu_treeview(self):
        self.ui.treeWidget_list.clear()
        self.ui.treeWidget_list.setColumnCount(1)
        self.ui.treeWidget_list.setHeaderLabels(["Project Tree"])

        for project in self.projects_names:
            project_item = QTreeWidgetItem(self.ui.treeWidget_list, [project])
            self.ui.treeWidget_list.addTopLevelItem(project_item)

            # Add child items for episodes, sequences, and shots
            for work_type in self.work_type_names:
                work_type_item = QTreeWidgetItem(project_item, [work_type])
                project_item.addChild(work_type_item)

                for episode in self.episode_names:
                    episode_item = QTreeWidgetItem(work_type_item, [episode])
                    work_type_item.addChild(episode_item)

                    for sequence in self.sequence_names:
                        sequence_item = QTreeWidgetItem(episode_item, [sequence])
                        episode_item.addChild(sequence_item)

                        for shot in self.shot_names:
                            shot_item = QTreeWidgetItem(sequence_item, [shot])
                            sequence_item.addChild(shot_item)

    def load_avatar_image(self, url):
        response = requests.get(url)
        response.raise_for_status()
        image_data = BytesIO(response.content)
        pixmap = QPixmap()
        pixmap.loadFromData(image_data.getvalue())
        scaled_pixmap = pixmap.scaled(25, 25, Qt.AspectRatioMode.KeepAspectRatio,
                                      Qt.TransformationMode.SmoothTransformation)
        self.ui.label_userimage.setPixmap(scaled_pixmap)
        self.ui.label_userimage.setFixedSize(25, 25)
        self.ui.label_userimage.setScaledContents(True)
# PyQt Program =====================================================================================
    def open_website(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            QDesktopServices.openUrl(QUrl("https://www.expiproject.com/"))  # Open URL

    def handle_quickscan(self):
        self.projects_names = self.handle_get_project()

        print ("Project Names:", self.projects_names)
        self.menu_quickSearch()
        self.menu_treeview()

    def handle_get_project(self):
        json_project_list = self.get_project_list(cookies=self.cookies)
        return [project['name'] for project in json_project_list['projects']]

    def handle_logout(self):
        # Logic for handling logout
        print("Logging out...")
        # RequestAPI.api_req_logout(self)
        self.cookies = None
        # Re-init login flow
        if not self.prelaunch():
            self.close()  # User cancelled login again

if __name__== "__main__":
    app = QApplication(sys.argv)
    ui = MainUI()
    ui.show()
    app.exec()