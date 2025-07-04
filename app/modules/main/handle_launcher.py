from PyQt6.QtCore import Qt, QStringListModel
from PyQt6.QtGui import QPixmap, QStandardItemModel, QStandardItem, QIcon
from PyQt6.QtWidgets import QWidget, QTreeWidgetItem, QListWidgetItem, QPushButton, QHeaderView, QStyleOptionButton, \
    QHBoxLayout, QAbstractItemView, QSizePolicy

from app.core.app_states import AppState
from app.services.asset import AssetService
from app.services.files import FileService
from app.services.project import ProjectService
from app.services.shot import ShotService
from app.services.task import TaskService
from app.ui.main.page.launcher_ui import Ui_Form
from app.services.auth import AuthServices

class LauncherHandler(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.project_data = None
        self.load_data()

        self.set_combobox_data()


# PyQt Program =====================================================================================
    def load_data(self):
        """Load data into the launcher"""

        all_data = []

        # Load projects
        project_list = ProjectService.get_user_project()
        for project in project_list:
            project_id = project.get("id")

            task_list = TaskService.get_task_types_by_project(project_id)
            asset_list = AssetService.get_asset_types_by_project(project_id)

            project_data = {
                "project_id": project_id,
                "project": project.get("name"),
                "episodes": [],
                "tasks": [
                    {"id": task["id"], "name": task["name"], "for_entity": task["for_entity"]}
                    for task in task_list
                ],
                "assets": [
                    {"id": asset["id"], "name": asset["name"]} for asset in asset_list
                ]
            }
            # Load episodes for each project
            episode_list = ShotService.get_episode_by_project(project_id)
            for episode in episode_list:
                episode_id = episode.get("id")
                episode_data = {
                    "episode_id": episode_id,
                    "episode": episode.get("name"),
                    "sequences": []
                }
                # Load sequences for each episode
                sequence_list = ShotService.get_sequence_by_episode(episode_id)
                for sequence in sequence_list:
                    sequence_id = sequence.get("id")
                    sequence_data = {
                        "sequence_id": sequence_id,
                        "sequence": sequence.get("name"),
                        "shots": []
                    }
                    # Load shots for each sequence
                    shots = ShotService.get_shots_by_sequence(sequence_id)
                    shot_data = []
                    for shot in shots:
                        shot_data.append({
                            "shot_id": shot.get("id"),
                            "shot": shot.get("name"),
                        })

                    sequence_data["shots"] = shot_data
                    episode_data["sequences"].append(sequence_data)
                project_data["episodes"].append(episode_data)
            all_data.append(project_data)
        self.project_data = all_data
        print(f"All Data: {all_data}")

    def set_combobox_data(self):
        """Set data for a combo box"""

        # Setup combo box awal
        self.ui.comboBox_project.clear()
        self.ui.comboBox_episode.clear()
        self.ui.comboBox_sequence.clear()
        self.ui.comboBox_shot.clear()

        # Isi project list
        for project in self.project_data:
            self.ui.comboBox_project.addItem(project["project"], project["project_id"])

        # Matikan semua selain project
        self.ui.comboBox_episode.setEnabled(False)
        self.ui.comboBox_task.setEnabled(False)
        self.ui.comboBox_sequence.setEnabled(False)
        self.ui.comboBox_shot.setEnabled(False)

        # Connect signals
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

        if project and project.get("episodes"):
            self.ui.comboBox_episode.setEnabled(True)
            for episode in project["episodes"]:
                self.ui.comboBox_episode.addItem(episode["episode"], episode["episode_id"])
        else:
            self.ui.comboBox_episode.setEnabled(False)

        if project and project.get("tasks"):
            self.ui.comboBox_task.setEnabled(True)
            for task in project["tasks"]:
                self.ui.comboBox_task.addItem(task["name"], task["id"])
        else:
            self.ui.comboBox_task.setEnabled(False)


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
