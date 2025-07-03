from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import QWidget, QTreeWidgetItem, QListWidgetItem, QPushButton, QHeaderView, QStyleOptionButton, \
    QHBoxLayout, QAbstractItemView

from app.services.task import TaskService
from app.ui.main.page.dashboard_ui import Ui_Form
from app.services.auth import AuthServices

class DashboardHandler(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.task_panel()

# PyQt Program =====================================================================================
    def task_panel(self):

        def task_table():
            headers = [
                "Project", "Type", "Status",
                "Entity", "Due Date",
                "Priority", "Comment By", "Last Comment"
            ]

            model = QStandardItemModel()
            model.setHorizontalHeaderLabels(headers)

            tasks = TaskService().get_table_task_list()
            for index, task in enumerate(tasks):
                if task.get("episode_name") is None or task.get("sequence_name") is None:
                    entity = f"{task.get("entity_type_name", "")} / {task.get("entity_name", "")}"
                else:
                    entity = f"{task.get("entity_type_name", "")} / {task.get('episode_name', '')} / {task.get('sequence_name', '')} / {task.get('entity_name', '')}"

                def make_non_editable_item(value):
                    item = QStandardItem(str(value))
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    return item

                item_project = QStandardItem(task["project_name"])
                item_project.setData(task["id"], Qt.ItemDataRole.UserRole)

                row = [
                    item_project,
                    QStandardItem(task["task_type_name"]),
                    QStandardItem(task["task_status_name"]),
                    QStandardItem(entity),
                    QStandardItem(str(task.get("due_date", ""))),
                    QStandardItem(str(task["priority"])),
                    QStandardItem(task.get("last_comment_person_full_name", "")),
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
            project_name = model.item(row, 0).text()
            print(f"Double-clicked row: {row}")
            print(f"Task ID: {task_id}")
            print(f"Project Name: {project_name}")
            # print(f"Loading details for task: {task.data(Qt.ItemDataRole.UserRole)}")

        task_table()