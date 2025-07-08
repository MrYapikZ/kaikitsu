import os
import sys

from PyQt6.QtCore import Qt, QStringListModel
from PyQt6.QtGui import QPixmap, QStandardItemModel, QStandardItem, QIcon
from PyQt6.QtWidgets import QWidget, QTreeWidgetItem, QListWidgetItem, QPushButton, QHeaderView, QStyleOptionButton, \
    QHBoxLayout, QAbstractItemView, QSizePolicy, QApplication, QMessageBox, QFileDialog

from app.ui.main.page.settings_ui import Ui_Form
from app.core.app_states import AppState
from app.services.asset import AssetService
from app.services.files import FileService
from app.services.project import ProjectService
from app.services.shot import ShotService
from app.services.task import TaskService
from app.services.auth import AuthServices
from app.services.kiyokai import KiyokaiService
from app.services.launcher.launcher_data import LauncherData
from app.utils.version_shots import VersionShotService

class SettingsHandler(QWidget):
    def __init__(self):
        super().__init__()

        # Load UI
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.project_data = AppState().project_data

        self.set_combobox_data()

        self.ui.pushButton_nasSave.clicked.connect(self.on_create_nas)
        self.ui.toolButton_locateFile.clicked.connect(self.open_file_dialog)
        self.ui.pushButton_shotCreate.clicked.connect(self.on_create_master_shot)
        self.ui.pushButton_shotUpdate.clicked.connect(self.on_update_master_shot)
        self.ui.pushButton_shotLoad.clicked.connect(self.on_load_master_shots)
        self.ui.toolButton_locateFolder.clicked.connect(self.open_folder_dialog)

    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select a File")
        if file_path:
            self.ui.lineEdit_locateFile.setText(file_path)
            print("Selected file:", file_path)

    def open_folder_dialog(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.ui.lineEdit_locateFolder.setText(folder_path)
            print("Selected folder:", folder_path)

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

        # Set map drive
        self.ui.comboBox_nasDrive.addItems([chr(letter) for letter in range(ord('A'), ord('Z') + 1)])

        # Set NAS server list
        self.set_combobox_nas_server()

    def set_combobox_nas_server(self):
        """Set NAS server list in comboBox"""
        try:
            response = KiyokaiService.get_nas_server_list()
            if response.get("success"):
                nas_servers = response.get("data", [])
                self.ui.comboBox_nas.clear()
                self.ui.comboBox_nasSettings.clear()
                for nas in nas_servers:
                    self.ui.comboBox_nas.addItem(nas["name"], nas["id"])
                    self.ui.comboBox_nasSettings.addItem(nas["name"], nas["id"])
            else:
                QMessageBox.warning(self, "Error", response.get("message", "Failed to fetch NAS servers."))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

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

    def on_create_nas(self):
        """Create NAS directory"""
        try:
            data = {
                "name": self.ui.lineEdit_nasName.text(),
                "host": self.ui.lineEdit_nasHost.text().strip(),
                "port": self.ui.spinBox_nasPort.value(),
                "username": self.ui.lineEdit_nasUsername.text(),
                "password": self.ui.lineEdit_nasPassword.text(),
                "project_path": self.ui.lineEdit_nasProjectPath.text().strip(),
                "drive_letter": self.ui.comboBox_nasDrive.currentText().strip(),
            }

            response = KiyokaiService.create_nas_server(data)
            if response.get("success"):
                QMessageBox.information(self, "Success", "NAS directory created successfully.")
            else:
                QMessageBox.warning(self, "Error", response.get("message", "Failed to create NAS directory."))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def on_create_master_shot(self):
        """Create Master Shot"""
        try:
            data = self.get_update_create_data()

            response = KiyokaiService.create_master_shot(data)
            if response.get("success"):
                # QMessageBox.information(self, "Success", "Master shot created successfully.")
                if self.ui.lineEdit_locateFolder.text().strip():
                    if self.show_question_popup("Create Version Shot?", "Do you also want to create a version shot for this master file?"):
                        self.pop_version_data(data, response.get("data").get("id"))
                else:
                    QMessageBox.information(self, "Success", "Master shot created successfully. Please load the master shot to create a version shot.")
            elif response.get("exists"):
                existing = response.get("data")
                QMessageBox.warning(self, "Warning", f"Master shot already exists:\n\n"
                                                     f"File Name: {existing.get('file_name')}\n"
                                                     f"File Path: {existing.get('file_path')}\n"
                                                     f"Task ID: {existing.get('task_name')}\n"
                                                     f"Shot ID: {existing.get('shot_name')}")
            else:
                QMessageBox.warning(self, "Error", response.get("message", "Failed to create master shot."))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def on_update_master_shot(self):
        """Update Master Shot"""
        try:
            task_index = self.ui.comboBox_task.currentIndex()
            shot_index = self.ui.comboBox_shot.currentIndex()

            task_id = self.ui.comboBox_task.itemData(task_index) if task_index >= 0 else None
            shot_id = self.ui.comboBox_shot.itemData(shot_index) if shot_index >= 0 else None

            file_path = self.ui.lineEdit_locateFile.text()
            file_name = file_path.split("/")[-1] if file_path else None
            version_folder = self.ui.lineEdit_locateFolder.text()

            data = {
                "file_name": file_name,
                "file_path": file_path,
                "version_folder": version_folder,
                "edit_user_id": AppState().user_data.get("user").get("id"),
                "edit_user_name": AppState().user_data.get("user").get("full_name"),
            }

            response = KiyokaiService.update_master_shot(shot_id=shot_id, task_id=task_id, data=data)
            if response.get("success"):
                # QMessageBox.information(self, "Success", "Master shot updated successfully.")
                if self.ui.lineEdit_locateFolder.text().strip():
                    if self.show_question_popup("Update Version Shot?", "Do you also want to update a version shot for this master file?"):
                        update_data = self.get_update_create_data()
                        self.pop_version_data(update_data, response.get("data").get("id"))
                else:
                    QMessageBox.information(self, "Success", "Master shot created successfully. Please load the master shot to create a version shot.")
            else:
                print(f"[-] Failed to get path data for Shot ID: {shot_id}, Task ID: {task_id}")
                if self.show_question_popup("MasterShot Missing",
                                            "Failed to get MasterShot data.\nDo you want to create a new MasterShot?"):
                    print("[!] Creating new MasterShot...")
                    self.on_create_master_shot()
                    return
                else:
                    print("[-] Quick pull operation cancelled.")
                    return
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def on_load_master_shots(self):
        """Load Master Shots"""
        try:
            task_index = self.ui.comboBox_task.currentIndex()
            shot_index = self.ui.comboBox_shot.currentIndex()
            task_id = self.ui.comboBox_task.itemData(task_index) if task_index >= 0 else None
            shot_id = self.ui.comboBox_shot.itemData(shot_index) if shot_index >= 0 else None

            response = KiyokaiService.get_master_shot_data_by_id(shot_id=shot_id, task_id=task_id)
            if response.get("success"):
                master_shots = response.get("data", {})
                self.ui.lineEdit_locateFile.setText(os.path.join(master_shots.get("file_path", ""), master_shots.get("file_name", "")) ) # NEED TO FIX
                self.ui.lineEdit_locateFolder.setText(master_shots.get("version_folder", ""))  # NEED TO FIX
            else:
                QMessageBox.warning(self, "Error", response.get("message", "Failed to load master shots."))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def update_version_shot(self, data: dict):
        """Update Version Shot"""
        try:
            version_folder = self.ui.lineEdit_locateFolder.text()

            normal, backup = VersionShotService.get_version_shot_data(version_folder)

            for version_number, files in normal.items():
                if not files:
                    continue

                # Get the only item from the dict
                file_name, file_path = next(iter(files.items()))

                version_data = data.copy()
                version_data["file_name"] = file_name
                version_data["file_path"] = file_path
                version_data["version_number"] = version_number

                response = KiyokaiService.create_version_shot(data=version_data)
                if response.get("success"):
                    print(f"[+] Version {version_number} - {file_name} created.")
                else:
                    print(f"[-] Failed to create Version {version_number}: {response.get('message', 'Unknown error')}")
            QMessageBox.information(self, "Success", "Version updated successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def get_update_create_data(self):
        """Get data for update or create Master Shot"""
        try:
            project_index = self.ui.comboBox_project.currentIndex()
            task_index = self.ui.comboBox_task.currentIndex()
            episode_index = self.ui.comboBox_episode.currentIndex()
            sequence_index = self.ui.comboBox_sequence.currentIndex()
            shot_index = self.ui.comboBox_shot.currentIndex()
            nas_index = self.ui.comboBox_nas.currentIndex()

            project_id = self.ui.comboBox_project.itemData(project_index)
            project_name = self.ui.comboBox_project.itemText(project_index)

            task_id = self.ui.comboBox_task.itemData(task_index) if task_index >= 0 else None
            task_name = self.ui.comboBox_task.itemText(task_index) if task_index >= 0 else None

            episode_id = self.ui.comboBox_episode.itemData(episode_index) if episode_index >= 0 else None
            episode_name = self.ui.comboBox_episode.itemText(episode_index) if episode_index >= 0 else None

            sequence_id = self.ui.comboBox_sequence.itemData(sequence_index) if sequence_index >= 0 else None
            sequence_name = self.ui.comboBox_sequence.itemText(sequence_index) if sequence_index >= 0 else None

            shot_id = self.ui.comboBox_shot.itemData(shot_index) if shot_index >= 0 else None
            shot_name = self.ui.comboBox_shot.itemText(shot_index) if shot_index >= 0 else None

            nas_id = self.ui.comboBox_nas.itemData(nas_index) if nas_index >= 0 else None
            nas_name = self.ui.comboBox_nas.itemText(nas_index) if nas_index >= 0 else None

            file_path = self.ui.lineEdit_locateFile.text()
            file_name = file_path.split("/")[-1] if file_path else None
            version_folder = self.ui.lineEdit_locateFolder.text()

            data = {
                "file_name": file_name,
                "file_path": file_path,
                "version_folder": version_folder,
                "edit_user_id": AppState().user_data.get("user").get("id"),
                "edit_user_name": AppState().user_data.get("user").get("full_name"),
                "project_id": project_id,
                "project_name": project_name,
                "task_id": task_id,
                "task_name": task_name,
                "episode_id": episode_id,
                "episode_name": episode_name,
                "sequence_id": sequence_id,
                "sequence_name": sequence_name,
                "shot_id": shot_id,
                "shot_name": shot_name,
                "nas_server_id": nas_id,
            }

            return data
        except Exception as e:
            print(f"[-] Error getting data for update/create Master Shot: {e}")

    def populate_from_quick_pull(self, project_id, task_id, episode_id, sequence_id, shot_id):
        """Populate Settings form with quick pull data for creating new MasterShot"""
        try:
            print(f"[+] Populating Settings with: Project:{project_id}, Task:{task_id}, Episode:{episode_id}, Sequence:{sequence_id}, Shot:{shot_id}")

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

            # Find and select the episode
            for i in range(self.ui.comboBox_episode.count()):
                if self.ui.comboBox_episode.itemData(i) == episode_id:
                    self.ui.comboBox_episode.setCurrentIndex(i)
                    break

            # Trigger episode changed to populate sequences
            self.on_episode_changed(self.ui.comboBox_episode.currentIndex())

            # Find and select the sequence
            for i in range(self.ui.comboBox_sequence.count()):
                if self.ui.comboBox_sequence.itemData(i) == sequence_id:
                    self.ui.comboBox_sequence.setCurrentIndex(i)
                    break

            # Trigger sequence changed to populate shots
            self.on_sequence_changed(self.ui.comboBox_sequence.currentIndex())

            # Find and select the shot
            for i in range(self.ui.comboBox_shot.count()):
                if self.ui.comboBox_shot.itemData(i) == shot_id:
                    self.ui.comboBox_shot.setCurrentIndex(i)
                    break

            print("[+] Settings form populated successfully with quick pull data")

        except Exception as e:
            print(f"[-] Error populating Settings form: {e}")

# Small Function =====================================================================================
    def pop_version_data(self, data, mastershot_id):
        """Pop and update version data"""
        version_data = data.copy()
        version_data.pop("file_name", None)
        version_data.pop("file_path", None)
        version_data.pop("nas_server_id", None)
        version_data.pop("version_folder", None)
        version_data["master_shot_id"] = mastershot_id
        self.update_version_shot(version_data)
