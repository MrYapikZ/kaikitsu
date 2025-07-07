import os.path
import sys

from PyQt6.QtCore import Qt, QStringListModel
from PyQt6.QtGui import QPixmap, QStandardItemModel, QStandardItem, QIcon
from PyQt6.QtWidgets import QWidget, QTreeWidgetItem, QListWidgetItem, QPushButton, QHeaderView, QStyleOptionButton, \
    QHBoxLayout, QAbstractItemView, QSizePolicy, QApplication, QMessageBox

from app.ui.main.page.launcher_ui import Ui_Form
from app.core.app_states import AppState
from app.services.asset import AssetService
from app.services.files import FileService
from app.services.project import ProjectService
from app.services.shot import ShotService
from app.services.task import TaskService
from app.services.auth import AuthServices
from app.services.kiyokai import KiyokaiService
from app.services.launcher.launcher_data import LauncherData
from app.utils.open_file import open_file_with_dialog

class LauncherHandler(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        AppState().set_project_data(LauncherData().load_data())

        self.project_data = AppState().project_data

        self.set_combobox_data()

        self.ui.pushButton_quickPull.clicked.connect(self.on_quick_pull)
        self.ui.pushButton_open.clicked.connect(self.on_open_file)

    def show_question_popup(self,title: str , message: str) -> bool:
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)

        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        response = msg_box.exec()

        return response == QMessageBox.StandardButton.Yes

# PyQt Program =====================================================================================

    def set_combobox_data(self):
        """Set data for a combo box"""

        # Clear comboBox
        self.ui.comboBox_project.clear()
        self.ui.comboBox_task.clear()
        self.ui.comboBox_episode.clear()
        self.ui.comboBox_sequence.clear()
        self.ui.comboBox_shot.clear()
        self.ui.comboBox_asset.clear()

        # Fill project list
        for project in self.project_data:
            self.ui.comboBox_project.addItem(project["project"], project["project_id"])

        # Disable all except project
        self.ui.comboBox_task.setEnabled(False)
        self.ui.comboBox_episode.setEnabled(False)
        self.ui.comboBox_sequence.setEnabled(False)
        self.ui.comboBox_shot.setEnabled(False)
        self.ui.comboBox_asset.setEnabled(False)

        # Hide all except project
        self.ui.comboBox_task.hide()
        self.ui.comboBox_episode.hide()
        self.ui.comboBox_sequence.hide()
        self.ui.comboBox_shot.hide()
        self.ui.comboBox_asset.hide()


        # Connect signals
        self.ui.comboBox_task.currentIndexChanged.connect(self.on_task_changed)
        self.ui.comboBox_project.currentIndexChanged.connect(self.on_project_changed)
        self.ui.comboBox_episode.currentIndexChanged.connect(self.on_episode_changed)
        self.ui.comboBox_sequence.currentIndexChanged.connect(self.on_sequence_changed)

    def set_tableview_detail(self, master_shot_data):
        if not master_shot_data:
            print("[-] No master shot data provided")
            return

        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Key", "Value"])

        field_map = {
            "file_name": "File Name",
            "file_path": "File Path",
            "project_name": "Project",
            "episode_name": "Episode",
            "sequence_name": "Sequence",
            "shot_name": "Shot",
            "task_name": "Task",
            "edit_user_name": "Last Edited By",
            "created_at": "Created At",
            "updated_at": "Updated At",
        }

        for key, label in field_map.items():
            value = master_shot_data.get(key, "")
            item_key = QStandardItem(label)
            item_value = QStandardItem(str(value))
            item_key.setEditable(False)
            item_value.setEditable(False)
            model.appendRow([item_key, item_value])

        # Add NAS server info if exists
        nas_data = master_shot_data.get("nas_server")
        if nas_data:
            nas_field_map = {
                "name": "NAS Name",
                # "host": "NAS Host",
                # "port": "NAS Port",
                # "username": "NAS Username",
                # "project_path": "NAS Project Path",
                "drive_letter": "NAS Drive Letter",
            }
            for key, label in nas_field_map.items():
                value = nas_data.get(key, "")
                item_key = QStandardItem(label)
                item_value = QStandardItem(str(value))
                item_key.setEditable(False)
                item_value.setEditable(False)
                model.appendRow([item_key, item_value])

        # Clear preview
        # self.ui.label_preview.clear()
        # self.ui.label_preview.setText("Preview")
        # self.ui.label_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Set table
        self.ui.tableView_metadataContent.setModel(model)
        self.ui.tableView_metadataContent.verticalHeader().setVisible(False)
        header = self.ui.tableView_metadataContent.horizontalHeader()
        self.ui.tableView_metadataContent.resizeColumnsToContents()
        for col in range(model.columnCount() - 1):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(model.columnCount() - 1, QHeaderView.ResizeMode.Stretch)

    def on_project_changed(self, index):
        self.ui.comboBox_episode.clear()
        self.ui.comboBox_task.clear()
        self.ui.comboBox_sequence.clear()
        self.ui.comboBox_shot.clear()

        self.ui.comboBox_sequence.setEnabled(False)
        self.ui.comboBox_shot.setEnabled(False)

        project_id = self.ui.comboBox_project.itemData(index)
        project = next((p for p in self.project_data if p["project_id"] == project_id), None)

        if project and project.get("tasks"):
            self.ui.comboBox_task.setEnabled(True)
            self.ui.comboBox_task.show()

            for task in project["tasks"]:
                self.ui.comboBox_task.addItem(task["task"], task["task_id"])
        else:
            self.ui.comboBox_task.setEnabled(False)

    def on_task_changed(self, index):
        self.ui.comboBox_asset.clear()
        self.ui.comboBox_episode.clear()
        self.ui.comboBox_sequence.clear()
        self.ui.comboBox_shot.clear()

        # Get project_id from comboBox_project
        project_index = self.ui.comboBox_project.currentIndex()
        project_id = self.ui.comboBox_project.itemData(project_index)
        task_id = self.ui.comboBox_task.itemData(index)

        # Get data project and task
        project = next((p for p in self.project_data if p["project_id"] == project_id), None)
        task = next((t for t in project["tasks"] if t["task_id"] == task_id), None) if project else None

        if not task:
            return

        entity = task.get("task_for_entity", "").lower()

        if entity == "asset":
            # Show combo asset
            self.ui.comboBox_asset.show()
            self.ui.comboBox_asset.setEnabled(True)

            # Hide episode, sequence, and shot
            self.ui.comboBox_episode.hide()
            self.ui.comboBox_sequence.hide()
            self.ui.comboBox_shot.hide()

            self.ui.comboBox_episode.setEnabled(False)
            self.ui.comboBox_sequence.setEnabled(False)
            self.ui.comboBox_shot.setEnabled(False)

            # Fill asset if exist
            if project and project.get("assets"):
                for asset in project["assets"]:
                    self.ui.comboBox_asset.addItem(asset["asset"], asset["asset_id"])
            else:
                self.ui.comboBox_asset.setEnabled(False)

        elif entity == "shot":
            # Show episode, sequence, shot
            self.ui.comboBox_episode.show()
            self.ui.comboBox_sequence.show()
            self.ui.comboBox_shot.show()

            self.ui.comboBox_asset.hide()
            self.ui.comboBox_asset.setEnabled(False)

            self.ui.comboBox_episode.setEnabled(True)
            self.ui.comboBox_sequence.setEnabled(False)
            self.ui.comboBox_shot.setEnabled(False)

            # Fill episode if exist
            if project and project.get("episodes"):
                for episode in project["episodes"]:
                    self.ui.comboBox_episode.addItem(episode["episode"], episode["episode_id"])
            else:
                self.ui.comboBox_episode.setEnabled(False)

    def on_episode_changed(self, index):
        self.ui.comboBox_sequence.clear()
        self.ui.comboBox_shot.clear()
        self.ui.comboBox_shot.setEnabled(False)

        project_index = self.ui.comboBox_project.currentIndex()
        project_id = self.ui.comboBox_project.itemData(project_index)
        episode_id = self.ui.comboBox_episode.itemData(index)

        project = next((p for p in self.project_data if p["project_id"] == project_id), None)
        episode = next((e for e in project["episodes"] if e["episode_id"] == episode_id), None) if project else None

        if episode and episode.get("sequences"):
            self.ui.comboBox_sequence.setEnabled(True)
            for seq in episode["sequences"]:
                self.ui.comboBox_sequence.addItem(seq["sequence"], seq["sequence_id"])
        else:
            self.ui.comboBox_sequence.setEnabled(False)

    def on_sequence_changed(self, index):
        self.ui.comboBox_shot.clear()

        project_index = self.ui.comboBox_project.currentIndex()
        episode_index = self.ui.comboBox_episode.currentIndex()
        project_id = self.ui.comboBox_project.itemData(project_index)
        episode_id = self.ui.comboBox_episode.itemData(episode_index)
        sequence_id = self.ui.comboBox_sequence.itemData(index)

        project = next((p for p in self.project_data if p["project_id"] == project_id), None)
        episode = next((e for e in project["episodes"] if e["episode_id"] == episode_id), None) if project else None
        sequence = next((s for s in episode["sequences"] if s["sequence_id"] == sequence_id),
                        None) if episode else None

        if sequence and sequence.get("shots"):
            self.ui.comboBox_shot.setEnabled(True)
            for shot in sequence["shots"]:
                self.ui.comboBox_shot.addItem(shot["shot"], shot["shot_id"])
        else:
            self.ui.comboBox_shot.setEnabled(False)

    def on_quick_pull(self):
        """Quick pull data from the selected project, task, episode, sequence, and shot"""

        project_index = self.ui.comboBox_project.currentIndex()
        task_index = self.ui.comboBox_task.currentIndex()
        episode_index = self.ui.comboBox_episode.currentIndex()
        sequence_index = self.ui.comboBox_sequence.currentIndex()
        shot_index = self.ui.comboBox_shot.currentIndex()

        project_id = self.ui.comboBox_project.itemData(project_index)
        task_id = self.ui.comboBox_task.itemData(task_index) if task_index >= 0 else None
        episode_id = self.ui.comboBox_episode.itemData(episode_index) if episode_index >= 0 else None
        sequence_id = self.ui.comboBox_sequence.itemData(sequence_index) if sequence_index >= 0 else None
        shot_id = self.ui.comboBox_shot.itemData(shot_index) if shot_index >= 0 else None

        if not project_id or not task_id or not episode_id or not sequence_id or not shot_id:
            print("[-] Please select all required fields: Project, Task, Episode, Sequence, and Shot.")
            return

        path_data = KiyokaiService().get_master_shot_data_by_id(shot_id, task_id)

        if not path_data or not path_data.get("success", False):
            print(f"[-] Failed to get path data for Shot ID: {shot_id}, Task ID: {task_id}")
            if self.show_question_popup("MasterShot Missing", "Failed to get MasterShot data.\nDo you want to create a new MasterShot?"):
                # Create new MasterShot logic here
                print("[!] Creating new MasterShot...")
                return
            else:
                print("[-] Quick pull operation cancelled.")
                return

        self.set_tableview_detail(path_data.get("data", {}))


        # Perform the quick pull operation here
        print(f"Quick Pull: Project ID: {project_id}, Task ID: {task_id}, Episode ID: {episode_id}, "
              f"Sequence ID: {sequence_id}, Shot ID: {shot_id}")

    def on_open_file(self):
        """Open the selected file using an OS-specific file dialog."""
        model = self.ui.tableView_metadataContent.model()

        if not model:
            print("[-] No metadata model available.")
            return

        file_path = None

        for row in range(model.rowCount()):
            key_index = model.index(row, 0)
            value_index = model.index(row, 1)
            key = model.data(key_index)
            value = model.data(value_index)

            if key == "File Path":
                file_path = value
                break  # found the value, stop searching

        if not file_path:
            print("[-] Missing file path.")
            return

        if not os.path.exists(file_path):
            print(f"[-] File does not exist: {file_path}")
            return

        open_file_with_dialog(file_path=file_path)