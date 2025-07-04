from PyQt6.QtCore import Qt, QStringListModel
from PyQt6.QtGui import QPixmap, QStandardItemModel, QStandardItem, QIcon
from PyQt6.QtWidgets import QWidget, QTreeWidgetItem, QListWidgetItem, QPushButton, QHeaderView, QStyleOptionButton, \
    QHBoxLayout, QAbstractItemView, QSizePolicy

from app.core.app_states import AppState
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

        self.load_data()

# PyQt Program =====================================================================================
    def load_data(self):
        """Load data into the launcher"""

        all_data = []

        # Load projects
        project_list = ProjectService.get_user_project()
        for project in project_list:
            project_id = project.get("id")
            project_data = {
                "project_id": project_id,
                "project": project.get("name"),
                "episodes": []
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
        print(f"All Data: {all_data}")