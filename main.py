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

class MainUI(QMainWindow):
    def __init__(self):
        super().__init__()

        # Instantiate and set up UI
        self.ui = MainWindowUI()
        self.ui.setupUi(self)

        # Cookies storage
        self.cookies = None

        # JSON data storage
        self.json_project_list = None
        self.json_metadata_list = None
        self.json_data_extract = None

        # User data
        self.username = None
        self.avatarUrl = ""

        # Quick Scan storage
        self.projects_names = set()
        self.episode_names = set()
        self.sequence_names = set()
        self.shot_names = set()
        self.work_type_names = set() #["Assets", "Animation", "Lighting", "Modeling", "Compositing"]

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

        self.handle_quickscan_pull()

        self.ui.treeWidget_list.itemDoubleClicked.connect(self.tree_item_double_clicked)

# UI Program ======================================================================================
    def menu_quicksearch(self):
        self.ui.comboBox_project.clear()
        self.ui.comboBox_workType.clear()
        self.ui.comboBox_episode.clear()
        self.ui.comboBox_sequence.clear()
        self.ui.comboBox_shot.clear()

        self.ui.comboBox_project.addItem("Select Project")
        for name in self.projects_names:
            self.ui.comboBox_project.addItem(name)

        self.ui.comboBox_workType.addItem("Select Work Type")
        self.ui.comboBox_episode.addItem("Select Episode")
        self.ui.comboBox_sequence.addItem("Select Sequence")
        self.ui.comboBox_shot.addItem("Select Shot")

        self.ui.comboBox_project.currentTextChanged.connect(self.menu_quicksearch_update_worktype)
        self.ui.comboBox_workType.currentTextChanged.connect(self.menu_quicksearch_update)
        self.ui.pushButton_qucikScan.clicked.connect(self.handle_quickscan_pull)

    def menu_quicksearch_update_worktype(self):
        self.ui.comboBox_workType.clear()
        self.ui.comboBox_workType.addItem("Select Work Type")

        selected_project = self.ui.comboBox_project.currentText()

        if self.json_data_extract and selected_project and selected_project != "Select Project":
            for work_type in self.json_data_extract[selected_project].keys():
                if work_type != "projectId":
                    self.ui.comboBox_workType.addItem(work_type)

        self.menu_quicksearch_update()

    def menu_quicksearch_update(self):
        self.ui.comboBox_episode.clear()
        self.ui.comboBox_sequence.clear()
        self.ui.comboBox_shot.clear()

        self.ui.comboBox_episode.addItem("Select Episode")
        self.ui.comboBox_sequence.addItem("Select Sequence")
        self.ui.comboBox_shot.addItem("Select Shot")

        selected_project = self.ui.comboBox_project.currentText()
        selected_work_type = self.ui.comboBox_workType.currentText()

        if not self.json_data_extract or selected_project not in self.json_data_extract:
            return

        project_data = self.json_data_extract[selected_project]
        if selected_work_type not in project_data or selected_work_type.lower() == "assets":
            return

        # Populate episodes
        for episode in project_data[selected_work_type].keys():
            self.ui.comboBox_episode.addItem(episode)

        # Optional: Auto-populate sequences/shots based on first episode
        def auto_fill_sequences():
            selected_work_type = self.ui.comboBox_workType.currentText()
            episode = self.ui.comboBox_episode.currentText()


            try:
                if selected_work_type and selected_work_type != "Select Work Type" and episode and episode != "Select Episode":
                    sequences = project_data[selected_work_type][episode]
                    self.ui.comboBox_sequence.clear()
                    self.ui.comboBox_sequence.addItem("Select Sequence")
                    for seq in sequences:
                        self.ui.comboBox_sequence.addItem(seq)
            except KeyError:
                pass

        def auto_fill_shots():
            selected_work_type = self.ui.comboBox_workType.currentText()
            episode = self.ui.comboBox_episode.currentText()
            sequence = self.ui.comboBox_sequence.currentText()


            try:
                if (selected_work_type and
                        selected_work_type != "Select Work Type" and
                        episode != "Select Episode" and
                        sequence != "Select Sequence" and
                        sequence in project_data[selected_work_type][episode]):
                    shots = project_data[selected_work_type][episode][sequence]
                    self.ui.comboBox_shot.clear()
                    self.ui.comboBox_shot.addItem("Select Shot")
                    for shot in shots:
                        self.ui.comboBox_shot.addItem(shot)
            except KeyError:
                pass

        self.ui.comboBox_episode.currentTextChanged.connect(auto_fill_sequences)
        self.ui.comboBox_sequence.currentTextChanged.connect(auto_fill_shots)

    def menu_treeview(self):
        self.ui.treeWidget_list.clear()
        self.ui.treeWidget_list.setColumnCount(1)
        self.ui.treeWidget_list.setHeaderLabels(["Project Tree"])

        for project in self.projects_names:
            if project not in self.json_data_extract:
                continue

            project_item = QTreeWidgetItem(self.ui.treeWidget_list, [project])
            self.ui.treeWidget_list.addTopLevelItem(project_item)

            project_data = self.json_data_extract[project]
            for work_type, work_data in project_data.items():
                if work_type == "projectId":
                    continue

                work_type_item = QTreeWidgetItem(project_item, [work_type])
                project_item.addChild(work_type_item)

                if work_type == "assets":
                    for asset_type, names in work_data.items():
                        asset_type_item = QTreeWidgetItem(work_type_item, [asset_type])
                        work_type_item.addChild(asset_type_item)

                        for asset_name, props in names.items():
                            name_item = QTreeWidgetItem(asset_type_item, [asset_name])
                            asset_type_item.addChild(name_item)
                            # name_item.addChild(QTreeWidgetItem(name_item, [f"itemId: {props.get('itemId', '')}"]))

                else:
                    for episode, sequences in work_data.items():
                        episode_item = QTreeWidgetItem(work_type_item, [f"ep{episode}"])
                        work_type_item.addChild(episode_item)

                        for sequence, shots in sequences.items():
                            sequence_item = QTreeWidgetItem(episode_item, [f"sq{sequence}"])
                            episode_item.addChild(sequence_item)

                            for shot, props in shots.items():
                                shot_item = QTreeWidgetItem(sequence_item, [f"sh{shot}"])
                                sequence_item.addChild(shot_item)

                                name = props.get("name", "")
                                # item_id = props.get("itemId", "")
                                if name:
                                    shot_item.addChild(QTreeWidgetItem(shot_item, [f"{name}"]))
                                # if item_id:
                                #     shot_item.addChild(QTreeWidgetItem(shot_item, [f"Item ID: {item_id}"]))

    def menu_metadata(self,project_id, metadata_id):
        self.ui.listWidget_metadataContent.clear()

        metadata_item = self.handle_get_metadata(project_id, metadata_id)
        metadata = metadata_item.get("metadata", {})
        # Add each metadata field to the QListWidget
        for key, value in metadata.items():
            self.ui.listWidget_metadataContent.addItem(f"{key}: {value}")

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

    def tree_item_double_clicked(self, item, column):
        names = []
        current = item
        while current is not None:
            names.insert(0, current.text(0))
            current = current.parent()

        if len(names) < 2:
            return

        project = names[0]
        work_type = names[1]

        project_id = self.json_data_extract.get(project, {}).get("projectId", "Unknown")

        try:
            if work_type == "assets":
                # Structure: project > assets > asset_type > asset_name
                if len(names) == 4:
                    asset_type = names[2]
                    asset_name = names[3]
                    item_id = self.json_data_extract[project][work_type][asset_type][asset_name]['itemId']
                    print(f"[Asset] Name: {asset_name} | Item ID: {item_id}")
            else:
                # Structure: project > work_type > epXXX > sqXXX > shXXX > name
                if len(names) == 6:
                    episode = names[2].replace("ep", "")
                    sequence = names[3].replace("sq", "")
                    shot = names[4].replace("sh", "")
                    name = names[5]
                    item_id = self.json_data_extract[project][work_type][episode][sequence][shot]['itemId']
                    print(f"[{work_type.title()}] Name: {name} | Item ID: {item_id} | Project ID: {project_id}")

                    self.menu_metadata(project_id, item_id)
        except KeyError as e:
            print("Could not locate item ID:", e)

    def handle_quickscan_pull(self):
        self.projects_names = self.handle_get_project()

        # selected_project = self.ui.comboBox_project.currentText()
        for project in self.json_project_list.get("projects", []):
            # if project["name"] == selected_project:
            self.json_data_extract = self.handle_get_metadata_list(project["id"], project["name"])


        print ("Project Names:", self.projects_names)
        self.menu_quicksearch()
        self.menu_treeview()

    def handle_get_project(self):
        self.json_project_list = RequestAPI.get_project_list(cookies=self.cookies)
        return [project['name'] for project in self.json_project_list['projects']]

    def handle_get_metadata(self, project_id, metadata_id):
        return RequestAPI.get_metadata(cookies=self.cookies, project_id=project_id, metadata_id=metadata_id)

    def handle_get_metadata_list(self, project_id, project_name):
        self.json_metadata_list = RequestAPI.get_metadata_list(cookies=self.cookies, project_id=project_id)
        return self.handle_extract_metadata(self.json_metadata_list, project_name, project_id, existing=self.json_data_extract)

    def handle_extract_metadata(self, metadata_list, project_name, project_id, existing=None):
        if existing is None:
            existing = {}

        if project_name not in existing:
            existing[project_name] = {
                "projectId": project_id
            }

        project = existing[project_name]

        for item in metadata_list.get("metadata", []):
            work_type = item.get("workType")
            item_id = item.get("id")
            name = item.get("name")

            if not work_type or not item_id:
                continue

            # ========================
            # For animation-like types
            # ========================
            if work_type != "assets":
                episode = item.get("episode")
                sequence = item.get("sequence")
                shot = item.get("shot")

                if not (episode and sequence and shot):
                    continue  # Ensure all levels exist

                if work_type not in project:
                    project[work_type] = {}

                if episode not in project[work_type]:
                    project[work_type][episode] = {}

                if sequence not in project[work_type][episode]:
                    project[work_type][episode][sequence] = {}

                project[work_type][episode][sequence][shot] = {
                    "name": name,
                    "itemId": item_id
                }

            # ====================
            # For assets or others
            # ====================
            else:
                asset_type = item.get("type") or "unknown"
                if not name:
                    continue

                if work_type not in project:
                    project[work_type] = {}

                if asset_type not in project[work_type]:
                    project[work_type][asset_type] = {}

                project[work_type][asset_type][name] = {
                    "itemId": item_id
                }

        print("Extracted Metadata:", existing)
        return existing

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