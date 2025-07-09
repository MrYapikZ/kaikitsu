import os.path
import sys
import re
import shutil

from PyQt6.QtCore import Qt, QStringListModel
from PyQt6.QtGui import QPixmap, QStandardItemModel, QStandardItem, QIcon
from PyQt6.QtWidgets import QWidget, QTreeWidgetItem, QListWidgetItem, QPushButton, QHeaderView, QStyleOptionButton, \
    QHBoxLayout, QAbstractItemView, QSizePolicy, QApplication, QMessageBox, QFileDialog

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
from app.utils.open_file import OpenFilePlatform
from app.utils.pyqt.text_wrap_delegate import TextWrapDelegate
from app.utils.blender import BlenderService

class LauncherHandler(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        AppState().set_project_data(LauncherData().load_data())

        self.project_data = AppState().project_data

        self.master_shot_id = ''

        self.set_combobox_data()

        self.ui.pushButton_quickPull.clicked.connect(self.on_quick_pull)
        self.ui.pushButton_open.clicked.connect(self.on_open_file)
        self.ui.listWidget_versions.itemDoubleClicked.connect(self.on_version_item_double_clicked)
        self.ui.pushButton_commit.clicked.connect(self.on_commit_version)
        self.ui.pushButton_push.clicked.connect(self.on_push_version)

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

    def show_version_action_popup(self, title: str, message: str) -> str:
        """
        Show a popup with three options:
        - Open Latest
        - Create New
        - Cancel

        Returns:
            "open" | "create" | "cancel"
        """
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)

        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)

        open_btn = msg_box.addButton("Open Latest", QMessageBox.ButtonRole.AcceptRole)
        create_btn = msg_box.addButton("Create New", QMessageBox.ButtonRole.DestructiveRole)
        cancel_btn = msg_box.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)

        msg_box.exec()

        if msg_box.clickedButton() == open_btn:
            return "latest"
        elif msg_box.clickedButton() == create_btn:
            return "create"
        else:
            return "cancel"

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

    def set_tableview_detail(self, master_shot_data, is_master_shot=True):
        if not master_shot_data:
            print("[-] No master shot data provided")
            return

        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Key", "Value"])

        field_map = {
            "id": "ID",
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

        if not is_master_shot:
            additional_field_map = {
                "version_number": "Version",
                "commited": "Committed",
                "locked": "Locked",
                "locked_by_user_name": "Locked By",
                "label": "Label",
                "notes": "Notes",
                "program": "Program",
            }
            field_map.update(additional_field_map)
        else:
            additional_field_map = {
                "version_folder": "Version Folder",
            }
            field_map.update(additional_field_map)

        for key, label in field_map.items():
            value = master_shot_data.get(key, "")
            item_key = QStandardItem(label)
            item_value = QStandardItem(str(value))
            item_key.setEditable(False)
            item_value.setEditable(False)
            model.appendRow([item_key, item_value])

        if is_master_shot:
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
        # self.ui.tableView_metadataContent.verticalHeader().setVisible(False)
        self.ui.tableView_metadataContent.setWordWrap(True)

        wrap_delegate = TextWrapDelegate(self.ui.tableView_metadataContent)
        self.ui.tableView_metadataContent.setItemDelegateForColumn(1, wrap_delegate)

        header = self.ui.tableView_metadataContent.horizontalHeader()
        self.ui.tableView_metadataContent.resizeColumnsToContents()
        for col in range(model.columnCount() - 1):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(model.columnCount() - 1, QHeaderView.ResizeMode.Stretch)

        self.ui.tableView_metadataContent.resizeRowsToContents()
        self.ui.tableView_metadataContent.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Interactive
        )

    def set_list_widget_versions(self, shot_id, task_id):
        """Set data for the list widget versions"""
        self.ui.listWidget_versions.clear()

        if not task_id or not shot_id:
            print("[-] Please select Project, Task, and Shot to view versions.")
            return

        try:
            # Fetch version data from KiyokaiService
            version_data = KiyokaiService().get_version_shot_by_shot_id(shot_id, task_id)

            if not version_data or not version_data.get("success", False):
                print(f"[-] Failed to get version data for Shot ID: {shot_id}, Task ID: {task_id}")
                return

            versions = version_data.get("data", [])
            if not versions:
                print("[-] No versions found for this shot.")
                return

            for version in versions:
                item = QListWidgetItem(f"v{version["version_number"]}")
                item.setData(Qt.ItemDataRole.UserRole, version["id"])
                self.ui.listWidget_versions.addItem(item)

            print(f"[+] Loaded {len(versions)} versions for Shot ID: {shot_id}")

        except Exception as e:
            print(f"[-] Error loading versions: {e}")

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
        self.master_shot_data = path_data.get("data", {})

        if not path_data or not path_data.get("success", False):
            print(f"[-] Failed to get path data for Shot ID: {shot_id}, Task ID: {task_id}")
            if self.show_question_popup("MasterShot Missing", "Failed to get MasterShot data.\nDo you want to create a new MasterShot?"):
                # Navigate to Settings tab and populate with quick pull data for creating new MasterShot
                print("[!] Creating new MasterShot...")
                self.navigate_to_settings_with_data(project_id, task_id, episode_id, sequence_id, shot_id)
                return
            else:
                print("[-] Quick pull operation cancelled.")
                return

        self.set_tableview_detail(path_data.get("data", {}))
        self.set_list_widget_versions(shot_id, task_id)

        # Perform the quick pull operation here
        print(f"Quick Pull: Project ID: {project_id}, Task ID: {task_id}, Episode ID: {episode_id}, "
              f"Sequence ID: {sequence_id}, Shot ID: {shot_id}")

    def on_open_file(self):
        """Open the selected file using an OS-specific file dialog."""
        id, data, file_path = self.patch_version_data("open")

        if not file_path:
            print("[-] Missing file path.")
            return

        if not os.path.exists(file_path):
            print(f"[-] File does not exist: {file_path}")
            return

        try:
            # Fetch version shot data using the ID
            version_shot_data = KiyokaiService().get_version_shot_by_version_id(id)
            if not version_shot_data or not version_shot_data.get("success", False):
                print(f"[-] Failed to open version shot data for ID: {id}")
                action =  self.show_version_action_popup(    "Version Conflict","The selected version shot could not be updated.\n\nWhat would you like to do?")
                if action == "latest":
                    self.open_latest_version(id)
                elif action == "create":
                    self.create_new_version(id)
                else:
                    print(f"[-] Cancel to open version shot data for ID: {id}")
                return
            else:
                # QMessageBox.information(self, "Success", "Version shot data fetched successfully.")
                if not version_shot_data.get("data", {}).get("locked", False) and not version_shot_data.get("data", {}).get("commited", False):
                    OpenFilePlatform.open_file_with_dialog(file_path=file_path)
                    KiyokaiService().update_version_shot_by_version_id(id, data)
                    print(f"[+] Opened file: {file_path}")
                else:
                    print(f"[-] Version shot data is locked or committed, cannot open file: {file_path}")
                    QMessageBox.warning(self, "Warning", "This version is locked or committed and cannot be opened.")
                    return
        except Exception as e:
            print(f"[-] Error fetching version shot data: {e}")
            QMessageBox.critical(self, "Error", f"Select version to commit version: {str(e)}")
            return

    def on_preview_open(self):
        """Pull master shot data and display in table view"""
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

        if not project_id or not task_id or not shot_id:
            print("[-] Please select all required fields: Project, Task, and Shot.")
            return

        try:
            # Pull data from KiyokaiService
            print(f"[+] Pulling master shot data for Shot ID: {shot_id}, Task ID: {task_id}")
            path_data = KiyokaiService().get_master_shot_data_by_id(shot_id, task_id)

            if path_data and path_data.get("success", False):
                # Display data in table view
                self.set_tableview_detail(path_data.get("data", {}))
                print(f"[+] Master shot data loaded successfully")
            else:
                print(f"[-] Failed to get path data for Shot ID: {shot_id}, Task ID: {task_id}")
                if self.show_question_popup("MasterShot Missing",
                                            "Failed to get MasterShot data.\nDo you want to create a new MasterShot?"):
                    # Navigate to Settings tab and populate with quick pull data for creating new MasterShot
                    print("[!] Creating new MasterShot...")
                    self.navigate_to_settings_with_data(project_id, task_id, episode_id, sequence_id, shot_id)
                    return
                else:
                    print("[-] Preview operation cancelled.")
                    return

        except Exception as e:
            print(f"[-] Error pulling master shot data: {e}")
            # Clear the table on error
            model = QStandardItemModel()
            model.setHorizontalHeaderLabels(["Key", "Value"])
            self.ui.tableView_metadataContent.setModel(model)

    def on_version_item_double_clicked(self, item: QListWidgetItem):
        version_id = item.data(Qt.ItemDataRole.UserRole)

        try:
            # Fetch version data from KiyokaiService
            version_data = KiyokaiService().get_version_shot_by_version_id(version_id)

            if not version_data or not version_data.get("success", False):
                print(f"[-] Failed to get version data for Version ID: {version_id}")
                return

            self.master_shot_id = version_data.get("data", {}).get("master_shot_id", "")
            self.set_tableview_detail(version_data.get("data", {}), False)

        except Exception as e:
            print(f"[-] Error opening version file: {e}")
            # Optionally, you can show a message box to the user
            QMessageBox.critical(self, "Error", f"Failed to open version file: {str(e)}")

    def on_commit_version(self):
        """Commit the selected version"""
        try:
            id, data, _ = self.patch_version_data("commit")

            try:
                # Fetch version shot data using the ID
                version_shot_data = KiyokaiService().update_version_shot_by_version_id(id, data)
                if not version_shot_data or not version_shot_data.get("success", False):
                    print(f"[-] Failed to get version shot data for ID: {id}")
                    return
                else:
                    QMessageBox.information(self, "Success", "Version shot data fetched successfully.")
            except Exception as e:
                print(f"[-] Error fetching version shot data: {e}")
                QMessageBox.critical(self, "Error", f"Select version to commit version: {str(e)}")
                return

            # Here you would typically commit the version using the fetched data
            # For demonstration, we will just print the data
            print(f"[+] Committing version for Version Shot ID: {self.master_shot_id}")

        except Exception as e:
            print(f"[-] Error committing version: {e}")
            # Optionally, you can show a message box to the user
            QMessageBox.critical(self, "Error", f"Failed to commit version: {str(e)}")

    def on_push_version(self):
        """Push the selected version"""
        try:
            id, data, _ = self.patch_version_data("push")

            try:
                # Fetch version shot data using the ID
                version_shot_data = KiyokaiService().update_version_shot_by_version_id(id, data)
                if not version_shot_data or not version_shot_data.get("success", False):
                    print(f"[-] Failed to get version shot data for ID: {id}")
                    return
                else:
                    QMessageBox.information(self, "Success", "Version shot data fetched successfully.")
            except Exception as e:
                print(f"[-] Error fetching version shot data: {e}")
                QMessageBox.critical(self, "Error", f"Select version to push version: {str(e)}")
                return

            # Here you would typically push the version using the fetched data
            # For demonstration, we will just print the data
            print(f"[+] Pushing version for Version Shot ID: {self.master_shot_id}")

        except Exception as e:
            print(f"[-] Error pushing version: {e}")
            # Optionally, you can show a message box to the user
            QMessageBox.critical(self, "Error", f"Failed to push version: {str(e)}")

    def navigate_to_settings_with_data(self, project_id, task_id, episode_id, sequence_id, shot_id):
        """Navigate to Settings tab and populate it with quick pull data"""
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
                            # Populate with quick pull data
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

    def populate_from_task_data(self, project_id, task_id, episode_id, sequence_id, shot_id, master_shot_data=None):
        """Populate Launcher form with task data from Dashboard"""
        try:
            print(f"[+] Populating Launcher with: Project:{project_id}, Task:{task_id}, Episode:{episode_id}, Sequence:{sequence_id}, Shot:{shot_id}")

            # Find and select the project
            for i in range(self.ui.comboBox_project.count()):
                if self.ui.comboBox_project.itemData(i) == project_id:
                    self.ui.comboBox_project.setCurrentIndex(i)
                    break

            # Trigger project changed to populate tasks
            self.on_project_changed(self.ui.comboBox_project.currentIndex())

            # Find and select the task
            for i in range(self.ui.comboBox_task.count()):
                if self.ui.comboBox_task.itemData(i) == task_id:
                    self.ui.comboBox_task.setCurrentIndex(i)
                    break

            # Trigger task changed to populate episodes/sequences/shots
            self.on_task_changed(self.ui.comboBox_task.currentIndex())

            # Find and select the episode if available
            if episode_id:
                for i in range(self.ui.comboBox_episode.count()):
                    if self.ui.comboBox_episode.itemData(i) == episode_id:
                        self.ui.comboBox_episode.setCurrentIndex(i)
                        break

                # Trigger episode changed to populate sequences
                self.on_episode_changed(self.ui.comboBox_episode.currentIndex())

            # Find and select the sequence if available
            if sequence_id:
                for i in range(self.ui.comboBox_sequence.count()):
                    if self.ui.comboBox_sequence.itemData(i) == sequence_id:
                        self.ui.comboBox_sequence.setCurrentIndex(i)
                        break

                # Trigger sequence changed to populate shots
                self.on_sequence_changed(self.ui.comboBox_sequence.currentIndex())

            # Find and select the shot if available
            if shot_id:
                for i in range(self.ui.comboBox_shot.count()):
                    if self.ui.comboBox_shot.itemData(i) == shot_id:
                        self.ui.comboBox_shot.setCurrentIndex(i)
                        break

            # Display master shot data if available
            if master_shot_data:
                self.master_shot_id = master_shot_data.get("id", "")
                self.set_tableview_detail(master_shot_data)
                self.set_list_widget_versions(shot_id, task_id)

            print("[+] Launcher form populated successfully with task data")

        except Exception as e:
            print(f"[-] Error populating Launcher form: {e}")

# Small Function =====================================================================================
    def patch_version_data(self, func_type):
        details_model = self.ui.tableView_metadataContent.model()
        if not details_model:
            print("[-] No details available. Please select a task first to populate details.")
            return

        # Extract task_id from details table
        id = None
        file_path = None
        for row in range(details_model.rowCount()):
            key_index = details_model.index(row, 0)
            value_index = details_model.index(row, 1)
            key = details_model.data(key_index)
            value = details_model.data(value_index)

            if key == "ID":
                id = value

            if func_type == "open" and key == "File Path":
                file_path = value

        if not id:
            print("[-] No Task ID found in details table")
            return

        data = {
            "edit_user_id": AppState().user_data.get("user").get("id"),
            "edit_user_name": AppState().user_data.get("user").get("full_name"),
        }

        if func_type == "open":
            data["locked"] = True
            data["locked_by_user_id"] = AppState().user_data.get("user").get("id")
            data["locked_by_user_name"] = AppState().user_data.get("user").get("full_name")
        elif func_type == "commit":
            data["locked"] = False
            data["locked_by_user_id"] = ""
            data["locked_by_user_name"] = ""
            data["label"] = self.ui.lineEdit_label.text()
            data["notes"] = self.ui.textEdit_note.toPlainText()
        elif func_type == "push":
            data["locked"] = False
            data["locked_by_user_id"] = ""
            data["locked_by_user_name"] = ""
            data["label"] = self.ui.lineEdit_label.text()
            data["notes"] = self.ui.textEdit_note.toPlainText()
            data["commited"] = True

        return id, data, file_path

    def open_latest_version(self, mastershot_id):
        """Open the latest version of the master shot"""
        try:
            # Fetch the latest version shot data
            master_shot = KiyokaiService().get_master_shot_by_master_shot_id(mastershot_id)

            if not master_shot or not master_shot.get("success", False):
                print(f"[-] Failed to get mastershot data for MasterShot ID: {mastershot_id}")
                return

            master_shot_data = master_shot.get("data", {})
            if not master_shot_data:
                print(f"[-] No version shot data found for MasterShot ID: {mastershot_id}")
                return

            latest_version = KiyokaiService().get_version_shot_by_version_id(master_shot_data.get("latest_version_shot").get("id"))
            file_path = latest_version.get("data").get("file_path", "")

            if not file_path or not os.path.exists(file_path):
                print(f"[-] File does not exist: {file_path}")
                return

            update_data = {
                "edit_user_id": AppState().user_data.get("user").get("id"),
                "edit_user_name": AppState().user_data.get("user").get("full_name"),
                "locked": True,
                "locked_by_user_id": AppState().user_data.get("user").get("id"),
                "locked_by_user_name": AppState().user_data.get("user").get("full_name"),
            }


            if not master_shot_data.get("latest_version_shot").get("locked", False) and not master_shot_data.get("latest_version_shot").get("commited", False):
                OpenFilePlatform.open_file_with_dialog(file_path=file_path)
                KiyokaiService().update_version_shot_by_version_id(master_shot_data.get("latest_version_shot").get("id"), update_data)
                print(f"[+] Opened latest version shot: {file_path}")
            else:
                print(f"[-] Latest version shot is locked or not committed: {file_path}")
                QMessageBox.warning(self, "Warning", "This version is locked or committed and cannot be opened.")

        except Exception as e:
            print(f"[-] Error opening latest version shot: {e}")

    def create_new_version(self, mastershot_id):
        """Create a new version for the master shot"""
        try:
            # Fetch the master shot data
            master_shot = KiyokaiService().get_master_shot_by_master_shot_id(mastershot_id)

            if not master_shot or not master_shot.get("success", False):
                print(f"[-] Failed to get mastershot data for MasterShot ID: {mastershot_id}")
                return

            master_shot_data = master_shot.get("data", {})
            if not master_shot_data:
                print(f"[-] No master shot data found for MasterShot ID: {mastershot_id}")
                return


            original_file_name = master_shot_data.get("file_name", "")
            master_file_path = master_shot_data.get("file_path", "")
            latest_version_shot = master_shot_data.get("latest_version_shot")
            latest_version = (
                latest_version_shot.get("version_number")
                if latest_version_shot and latest_version_shot.get("version_number") is not None
                else 0
            )
            version_str = f"{latest_version:03d}"

            new_file_name = re.sub(r'(_[^_]+)(\.\w+)$', rf'_v{version_str}\2', original_file_name)
            file_ext = os.path.splitext(original_file_name)[1].lower()

            version_folder = master_shot_data.get("version_folder")
            if not version_folder:
                base_folder = master_file_path
                version_folder = os.path.join(base_folder, "versions")

            if not os.path.exists(version_folder):
                os.makedirs(version_folder, exist_ok=True)

            version_file_path = os.path.join(version_folder, new_file_name)

            if file_ext == ".blend":
                # Ask user to locate Blender executable
                blender_path, _ = QFileDialog.getOpenFileName(
                    self, "Select Blender Executable", "", "Blender Executable (*.exe *.app *.bin);;All Files (*.*)"
                )
                if not blender_path:
                    QMessageBox.warning(self, "Missing Blender", "Blender executable not selected.")
                    return
                if blender_path.endswith(".app"):
                    blender_path = os.path.join(blender_path, "Contents", "MacOS", "Blender")
                blender_save_as = BlenderService().save_as_blend_file(blender_path, master_file_path, version_file_path)
                if blender_save_as.get("success", True):
                    print(f"[+] Blender project saved as: {version_file_path}")
                else:
                    print(f"[-] Failed to save Blender project: {blender_save_as.get('message', 'Unknown error')}")
                    QMessageBox.warning(self, "Warning", "Failed to save Blender project.")
                    return
            else:
                shutil.copy2(master_file_path, version_file_path)
                print(f"[+] File copied to: {version_file_path}")

            new_version_data = {
                "file_name": new_file_name,
                "file_path": version_file_path,
                "edit_user_id": AppState().user_data.get("user").get("id"),
                "edit_user_name": AppState().user_data.get("user").get("full_name"),
                "master_shot_id": mastershot_id,
                "project_id": master_shot_data.get("project_id"),
                "project_name": master_shot_data.get("project_name"),
                "episode_id": master_shot_data.get("episode_id"),
                "episode_name": master_shot_data.get("episode_name"),
                "sequence_id": master_shot_data.get("sequence_id"),
                "sequence_name": master_shot_data.get("sequence_name"),
                "shot_id": master_shot_data.get("shot_id"),
                "shot_name": master_shot_data.get("shot_name"),
                "task_id": master_shot_data.get("task_id"),
                "task_name": master_shot_data.get("task_name"),
            }

            new_version = KiyokaiService().create_version_shot(new_version_data)
            if not new_version or not new_version.get("success", False):
                print(f"[-] Failed to create new version shot for MasterShot ID: {mastershot_id}")
                return

            print(f"[+] Created new version shot successfully: {new_version.get('data').get('id')}")

            update_data = {
                "edit_user_id": AppState().user_data.get("user").get("id"),
                "edit_user_name": AppState().user_data.get("user").get("full_name"),
                "locked": True,
                "locked_by_user_id": AppState().user_data.get("user").get("id"),
                "locked_by_user_name": AppState().user_data.get("user").get("full_name"),
            }
            OpenFilePlatform.open_file_with_dialog(file_path=version_file_path)
            KiyokaiService().update_version_shot_by_version_id(new_version.get("data").get("id"), update_data)
            print(f"[+] Opened latest version shot: {version_file_path}")

        except Exception as e:
            print(f"[-] Error creating new version shot: {e}")