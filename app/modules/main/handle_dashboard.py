from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget, QTreeWidgetItem, QListWidgetItem
from app.ui.main.page.dashboard_ui import Ui_Form
from app.services.auth import AuthServices

class DashboardHandler(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

