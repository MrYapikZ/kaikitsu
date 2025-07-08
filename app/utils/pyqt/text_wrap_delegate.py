from PyQt6.QtWidgets import QStyledItemDelegate
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QFontMetrics


class TextWrapDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def paint(self, painter, option, index):
        option.textElideMode = Qt.TextElideMode.ElideNone
        option.displayAlignment = Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        super().paint(painter, option, index)

    def sizeHint(self, option, index):
        text = index.data()
        font_metrics = QFontMetrics(option.font)
        text_width = option.rect.width()
        text_height = font_metrics.boundingRect(0, 0, text_width, 1000, Qt.TextFlag.TextWordWrap, text).height()
        return QSize(text_width, text_height + 10)