from PyQt6.QtCore import Qt, QStringListModel
from PyQt6.QtGui import QPixmap, QStandardItemModel, QStandardItem, QIcon
from PyQt6.QtWidgets import QWidget, QTreeWidgetItem, QListWidgetItem, QPushButton, QHeaderView, QStyleOptionButton, \
    QHBoxLayout, QAbstractItemView, QSizePolicy

from app.core.app_states import AppState
from app.services.files import FileService
from app.services.task import TaskService
from app.ui.main.page.dashboard_ui import Ui_Form
from app.services.auth import AuthServices

class DashboardHandler(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.tasks = None

        self.task_refresh()

# PyQt Program =====================================================================================
    def task_refresh(self):
        """Refresh the task list"""
        self.tasks = TaskService().get_table_task_list()
        AppState().set_task_data(self.tasks)
        self.task_panel()

    def task_panel(self):

        def task_table():
            headers = [
                "Project", "Type", "Status",
                "Entity", "Due Date",
                "Priority", "Comment By", "Last Comment"
            ]

            model = QStandardItemModel()
            model.setHorizontalHeaderLabels(headers)

            if not self.tasks:
                print("[-] No tasks found.")
                self.ui.tableView_task.setModel(model)
                return

            for index, task in enumerate(self.tasks):
                if task.get("episode_name") and task.get("sequence_name"):
                    entity = f"{task.get('entity_type_name', '')} / {task.get('episode_name', '')} / {task.get('sequence_name', '')} / {task.get('entity_name', '')}"
                else:
                    entity = f"{task.get('entity_type_name', '')} / {task.get('entity_name', '')}"

                item_project = QStandardItem(task["project_name"])
                item_project.setData(task["id"], Qt.ItemDataRole.UserRole)

                item_user = QStandardItem(task.get("last_comment_person_full_name", ""))
                if task.get("last_comment_person_avatar_path", ""):
                    item_user.setIcon(QIcon(task.get("last_comment_person_avatar_path", "")))

                row = [
                    item_project,
                    QStandardItem(task["task_type_name"]),
                    QStandardItem(task["task_status_name"]),
                    QStandardItem(entity),
                    QStandardItem(str(task.get("due_date", ""))),
                    QStandardItem(str(task["priority"])),
                    item_user,
                    QStandardItem(task.get("last_comment_text", ""))
                ]
                model.appendRow(row)

            self.ui.tableView_task.setModel(model)
            self.ui.tableView_task.resizeColumnsToContents()
            self.ui.tableView_task.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            # self.ui.tableView_task.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
            header = self.ui.tableView_task.horizontalHeader()
            self.ui.tableView_task.resizeColumnsToContents()
            for col in range(model.columnCount() - 1):
                header.setSectionResizeMode(col, QHeaderView.ResizeMode.Interactive)
            header.setSectionResizeMode(model.columnCount() - 1, QHeaderView.ResizeMode.Stretch)

            self.ui.tableView_task.doubleClicked.connect(load_details)

        def load_details(task):
            """Load task details in a new window or dialog"""
            # This function should be implemented to show task details
            row = task.row()
            model = self.ui.tableView_task.model()
            task_id = model.item(row, 0).data(Qt.ItemDataRole.UserRole)

            self.details_panel(task_id)

            # print(f"Loading details for task: {task.data(Qt.ItemDataRole.UserRole)}")

        self.ui.pushButton_taskRefresh.clicked.connect(self.task_refresh)

        task_table()

    def details_panel(self, task_id):
        """
        This function is a placeholder for the details panel.
        It can be implemented to show detailed information about a selected task.
        """
        # Implement the details panel logic here
        def details_widget(task_id):
            task_data = next((task for task in self.tasks if task["id"] == task_id), None)

            if not task_data:
                print(f"[-] No task found with ID: {task_id}")
                return

            model = QStandardItemModel()
            model.setHorizontalHeaderLabels(["Key", "Value"])
            field_map = {
                "id": "Task ID",
                "project_name": "Project",
                "task_type_name": "Type",
                "task_status_name": "Status",
                # "episode_name": "Episode",
                # "sequence_name": "Sequence",
                "entity_name": "Entity",
                # "entity_type_name": "Entity Type",
                "due_date": "Due Date",
                "priority": "Priority",
                "last_comment_person_full_name": "Comment By",
                "last_comment_text": "Last Comment",
                # "last_comment_person_avatar_path": "Avatar Path"
            }

            for key, label in field_map.items():
                value = task_data.get(key, "")
                item_key = QStandardItem(label)
                if key == "entity_name":
                    if task_data.get("episode_name") and task_data.get("sequence_name"):
                        entity = f"{task_data.get('entity_type_name', '')} / {task_data.get('episode_name', '')} / {task_data.get('sequence_name', '')} / {task_data.get('entity_name', '')}"
                    else:
                        entity = f"{task_data.get('entity_type_name', '')} / {task_data.get('entity_name', '')}"
                    item_value = QStandardItem(entity)
                elif key == "last_comment_person_full_name" and value:
                    item_value = QStandardItem(task_data.get("last_comment_person_full_name", ""))
                    if task_data.get("last_comment_person_avatar_path", ""):
                        item_value.setIcon(QIcon(task_data.get("last_comment_person_avatar_path", "")))
                else:
                    item_value = QStandardItem(str(value))

                # Optional: make them not editable
                item_key.setEditable(False)
                item_value.setEditable(False)

                model.appendRow([item_key, item_value])

            if task_data.get("entity_preview_file_id"):
                preview_file_path = FileService.get_preview_file_thumbnail(task_data.get("entity_preview_file_id"))

                if preview_file_path["success"] is True:
                    pixmap = QPixmap(preview_file_path.get("file_path", ""))
                    if not pixmap.isNull():  # Check if image loaded successfully
                        label_width = self.ui.label_preview.width()
                        if label_width == 0:
                            label_width = 200  # fallback default width

                        # Hitung tinggi yang sesuai dengan aspect ratio
                        aspect_ratio = pixmap.height() / pixmap.width()
                        label_height = int(label_width * aspect_ratio)

                        scaled_pixmap = pixmap.scaled(
                            label_width, label_height,
                            Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.SmoothTransformation
                        )

                        self.ui.label_preview.setPixmap(scaled_pixmap)
                        self.ui.label_preview.setFixedHeight(label_height)
                        self.ui.label_preview.setScaledContents(False)
                        self.ui.label_preview.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
                    else:
                        print(f"[-] Failed to load avatar image from: {preview_file_path}")
            else:
                self.ui.label_preview.clear()
                self.ui.label_preview.setText("Preview")
                self.ui.label_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)

            self.ui.tableView_details.setModel(model)
            self.ui.tableView_details.verticalHeader().setVisible(False)
            header = self.ui.tableView_details.horizontalHeader()
            self.ui.tableView_details.resizeColumnsToContents()
            for col in range(model.columnCount() - 1):
                header.setSectionResizeMode(col, QHeaderView.ResizeMode.Interactive)
            header.setSectionResizeMode(model.columnCount() - 1, QHeaderView.ResizeMode.Stretch)

        details_widget(task_id)
