import os
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QWidget


class SelectBlenderService:
    def __init__(self, parent: QWidget = None):
        self.parent = parent  # Use QWidget or None

    def select_blender(self):
        """Open dialog to select Blender executable manually."""
        blender_path, _ = QFileDialog.getOpenFileName(
            self.parent,
            "Select Blender Executable",
            "",
            "Blender Executable (*.exe *.app *.bin);;All Files (*)"
        )

        if not blender_path:
            QMessageBox.warning(self.parent, "Missing Blender", "Blender executable not selected.")
            return None

        # macOS `.app` fix (navigate inside app bundle)
        if blender_path.endswith(".app"):
            blender_path = os.path.join(blender_path, "Contents", "MacOS", "Blender")

        return os.path.abspath(blender_path)