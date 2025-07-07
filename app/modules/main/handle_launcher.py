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

class LauncherHandler(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.project_data = LauncherData().load_data()

        self.set_combobox_data()

        self.ui.pushButton_quickPull.clicked.connect(self.quick_pull)

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

    def quick_pull(self):
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

        print("PATH DATA:", path_data)


        # Perform the quick pull operation here
        print(f"Quick Pull: Project ID: {project_id}, Task ID: {task_id}, Episode ID: {episode_id}, "
              f"Sequence ID: {sequence_id}, Shot ID: {shot_id}")