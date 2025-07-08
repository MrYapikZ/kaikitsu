from PyQt6.QtCore import Qt, QStringListModel
from PyQt6.QtGui import QPixmap, QStandardItemModel, QStandardItem, QIcon
from PyQt6.QtWidgets import QWidget, QTreeWidgetItem, QListWidgetItem, QPushButton, QHeaderView, QStyleOptionButton, \
    QHBoxLayout, QAbstractItemView, QSizePolicy, QApplication, QMessageBox

from app.core.app_states import AppState
from app.services.files import FileService
from app.services.shot import ShotService
from app.services.task import TaskService
from app.services.kiyokai import KiyokaiService
from app.ui.main.page.dashboard_ui import Ui_Form
from app.services.auth import AuthServices
from app.utils.pyqt.text_wrap_delegate import TextWrapDelegate

class DashboardHandler(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.tasks = None

        self.task_refresh()

        self.ui.pushButton_previewOpen.clicked.connect(self.on_preview_open)

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

            # Check if tasks is None, empty, or not a list
            if not self.tasks or not isinstance(self.tasks, list):
                print("[-] No tasks found or invalid task data.")
                self.ui.tableView_task.setModel(model)
                return

            for index, task in enumerate(self.tasks):
                # Validate that task is a dictionary
                if not isinstance(task, dict):
                    print(f"[-] Invalid task data at index {index}: {task}")
                    continue

                # Safely get entity information
                try:
                    if task.get("episode_name") and task.get("sequence_name"):
                        entity = f"{task.get('entity_type_name', '')} / {task.get('episode_name', '')} / {task.get('sequence_name', '')} / {task.get('entity_name', '')}"
                    else:
                        entity = f"{task.get('entity_type_name', '')} / {task.get('entity_name', '')}"
                except Exception as e:
                    print(f"[-] Error processing entity for task {index}: {e}")
                    entity = "Unknown Entity"

                # Safely create table items with default values
                try:
                    item_project = QStandardItem(task.get("project_name", "Unknown Project"))
                    item_project.setData(task.get("id", ""), Qt.ItemDataRole.UserRole)

                    item_user = QStandardItem(task.get("last_comment_person_full_name", ""))
                    if task.get("last_comment_person_avatar_path", ""):
                        try:
                            item_user.setIcon(QIcon(task.get("last_comment_person_avatar_path", "")))
                        except Exception as icon_error:
                            print(f"[-] Could not load avatar icon: {icon_error}")

                    row = [
                        item_project,
                        QStandardItem(task.get("task_type_name", "")),
                        QStandardItem(task.get("task_status_name", "")),
                        QStandardItem(entity),
                        QStandardItem(str(task.get("due_date", ""))),
                        QStandardItem(str(task.get("priority", ""))),
                        item_user,
                        QStandardItem(task.get("last_comment_text", ""))
                    ]
                    model.appendRow(row)
                except Exception as e:
                    print(f"[-] Error creating table row for task {index}: {e}")
                    continue

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
            try:
                row = task.row()
                model = self.ui.tableView_task.model()
                task_id = model.item(row, 0).data(Qt.ItemDataRole.UserRole)

                if task_id:
                    self.details_panel(task_id)
                else:
                    print("[-] No task ID found for selected row")
            except Exception as e:
                print(f"[-] Error loading task details: {e}")

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
            # self.ui.tableView_details.verticalHeader().setVisible(False)
            self.ui.tableView_details.setWordWrap(True)

            wrap_delegate = TextWrapDelegate(self.ui.tableView_details)
            self.ui.tableView_details.setItemDelegateForColumn(1, wrap_delegate)

            header = self.ui.tableView_details.horizontalHeader()
            self.ui.tableView_details.resizeColumnsToContents()
            for col in range(model.columnCount() - 1):
                header.setSectionResizeMode(col, QHeaderView.ResizeMode.Interactive)
            header.setSectionResizeMode(model.columnCount() - 1, QHeaderView.ResizeMode.Stretch)

            self.ui.tableView_details.resizeRowsToContents()
            self.ui.tableView_details.verticalHeader().setSectionResizeMode(
                QHeaderView.ResizeMode.Interactive
            )

        details_widget(task_id)

    def show_question_popup(self, title: str, message: str) -> bool:
        """Show a question popup dialog"""
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        response = msg_box.exec()
        return response == QMessageBox.StandardButton.Yes

    def navigate_to_launcher_with_data(self, project_id, task_id, episode_id, sequence_id, shot_id, master_shot_data=None):
        """Navigate to Launcher tab and populate it with task data"""
        try:
            # Find the main window and tab widget
            main_window = self.window()
            if hasattr(main_window, 'ui') and hasattr(main_window.ui, 'tabWidget'):
                tab_widget = main_window.ui.tabWidget

                # Find the Launcher tab
                for i in range(tab_widget.count()):
                    if tab_widget.tabText(i) == "Launcher":
                        # Switch to Launcher tab
                        tab_widget.setCurrentIndex(i)

                        # Get the Launcher handler widget
                        launcher_widget = tab_widget.widget(i)
                        if hasattr(launcher_widget, 'populate_from_task_data'):
                            # Populate with task data
                            launcher_widget.populate_from_task_data(project_id, task_id, episode_id, sequence_id, shot_id, master_shot_data)
                        elif hasattr(launcher_widget, 'set_tableview_detail') and master_shot_data:
                            # Just set the table view detail if populate method doesn't exist
                            launcher_widget.set_tableview_detail(master_shot_data)
                        else:
                            print("[-] Launcher widget doesn't have required methods")
                        break
                else:
                    print("[-] Launcher tab not found")
            else:
                print("[-] Could not find main window tab widget")
        except Exception as e:
            print(f"[-] Error navigating to Launcher: {e}")

    def navigate_to_settings_with_data(self, project_id, task_id, episode_id, sequence_id, shot_id):
        """Navigate to Settings tab and populate it with task data for creating new MasterShot"""
        try:
            # Find the main window and tab widget
            main_window = self.window()
            if hasattr(main_window, 'ui') and hasattr(main_window.ui, 'tabWidget'):
                tab_widget = main_window.ui.tabWidget

                # Find the Settings tab
                for i in range(tab_widget.count()):
                    if tab_widget.tabText(i) == "Settings":
                        # Switch to Settings tab
                        tab_widget.setCurrentIndex(i)

                        # Get the Settings handler widget
                        settings_widget = tab_widget.widget(i)
                        if hasattr(settings_widget, 'populate_from_quick_pull'):
                            # Populate with task data
                            settings_widget.populate_from_quick_pull(project_id, task_id, episode_id, sequence_id, shot_id)
                        else:
                            print("[-] Settings widget doesn't have populate_from_quick_pull method")
                        break
                else:
                    print("[-] Settings tab not found")
            else:
                print("[-] Could not find main window tab widget")
        except Exception as e:
            print(f"[-] Error navigating to Settings: {e}")

    def on_preview_open(self):
        """Open preview - navigate to Launcher and pull master shot data"""
        # Get task ID from the details table instead of task table
        details_model = self.ui.tableView_details.model()
        if not details_model:
            print("[-] No details available. Please select a task first to populate details.")
            return

        # Extract task_id from details table
        task_id = None
        for row in range(details_model.rowCount()):
            key_index = details_model.index(row, 0)
            value_index = details_model.index(row, 1)
            key = details_model.data(key_index)
            value = details_model.data(value_index)

            if key == "Task ID":
                task_id = value
                break

        if not task_id:
            print("[-] No Task ID found in details table")
            return

        # Find the task data using the task_id from details
        task_data = next((task for task in self.tasks if task["id"] == task_id), None)
        if not task_data:
            print(f"[-] No task found with ID: {task_id}")
            return



        # Extract required IDs from task data
        project_id = task_data.get("project_id")
        episode_id = task_data.get("episode_id")
        sequence_data = ShotService.get_sequence_by_name(project_id,episode_id,task_data.get("sequence_name"))
        if sequence_data:
            sequence_id = sequence_data.get("id")
        else :
            sequence_id = None
        shot_id = task_data.get("entity_id")  # Assuming entity_id is the shot_id for shots
        task_type_id = task_data.get("task_type_id")

        if not all([project_id, task_id, shot_id, task_type_id]):
            print("[-] Missing required IDs in task data")
            print(f"Project ID: {project_id}, Task ID: {task_id}, Shot ID: {shot_id}")
            return

        try:
            # Pull master shot data from KiyokaiService
            print(f"[+] Pulling master shot data for Shot ID: {shot_id}, Task ID: {task_type_id}")
            path_data = KiyokaiService().get_master_shot_data_by_id(shot_id=shot_id, task_id=task_type_id)

            if path_data and path_data.get("success", False):
                # Navigate to Launcher and display the data
                self.navigate_to_launcher_with_data(
                    project_id, task_type_id, episode_id, sequence_id, shot_id,
                    path_data.get("data", {})
                )
                print(f"[+] Successfully navigated to Launcher with master shot data")
            else:
                print(f"[-] Failed to get path data for Shot ID: {shot_id}, Task ID: {task_id}")
                if self.show_question_popup("MasterShot Missing", "Failed to get MasterShot data.\nDo you want to create a new MasterShot?"):
                    # Navigate to Settings tab and populate with task data for creating new MasterShot
                    print("[!] Creating new MasterShot...")
                    self.navigate_to_settings_with_data(project_id, task_type_id, episode_id, sequence_id, shot_id)
                    return
                else:
                    print("[-] Preview operation cancelled.")
                    return

        except Exception as e:
            print(f"[-] Error pulling master shot data: {e}")
            # Navigate to Launcher anyway to show the interface
            self.navigate_to_launcher_with_data(project_id, task_id, episode_id, sequence_id, shot_id)
