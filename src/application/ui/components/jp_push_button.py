from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush
from PyQt5.QtCore import Qt, QRectF

from application.ui.components.jumping_machine import JumpingMachine

from typing import Dict

class JpPushButton(QPushButton, JumpingMachine):

    thickness: int = 5

    color_mode: Dict[bool, QColor] = {
        False: QColor(0, 0, 0),
        True: QColor(255, 0, 0),
    }


    def __init__(self, parent=None):
        super().__init__( parent=parent, text="None",  parentJP=parent, instanceJP=self)

        self.FLAG_is_object_selected = False
        self.color_normal = QColor(34, 198, 78)
        self.color_selected = QColor(255, 0, 0)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        is_pressed = self.isDown()
        border_color = self.color_mode[self.FLAG_is_object_selected]

        bg_color =  self.color_selected if is_pressed else self.color_normal

        offset = self.thickness / 2
        rect = QRectF(self.rect()).adjusted(offset, offset, -offset, -offset)

        painter.setBrush(QBrush(bg_color))
        pen = QPen(border_color)
        pen.setWidth(self.thickness)
        painter.setPen(pen)

        painter.drawRoundedRect(rect, 10.0, 10.0)

        if is_pressed:
            painter.translate(0, 1)

        painter.setPen(QColor(255, 255, 255))
        painter.setFont(self.font())
        painter.drawText(self.rect(), Qt.AlignCenter, self.text())
