from PyQt6.QtWidgets import QWidget
from app.ui.main.page.launcher_ui import Ui_Form
from app.services.auth import AuthServices

class LauncherHandler(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
