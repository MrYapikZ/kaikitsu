import requests
from io import BytesIO
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap


def load_avatar_image(self, url):
    response = requests.get(url)
    response.raise_for_status()
    image_data = BytesIO(response.content)
    pixmap = QPixmap()
    pixmap.loadFromData(image_data.getvalue())
    scaled_pixmap = pixmap.scaled(25, 25, Qt.AspectRatioMode.KeepAspectRatio,
                                  Qt.TransformationMode.SmoothTransformation)
    self.ui.label_userimage.setPixmap(scaled_pixmap)
    self.ui.label_userimage.setFixedSize(25, 25)
    self.ui.label_userimage.setScaledContents(True)