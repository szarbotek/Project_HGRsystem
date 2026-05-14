from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QFont, QPen
from PyQt5.QtCore import Qt, QRectF

class DisplayData(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.background_color = QColor(172, 83, 30)## dark orange
        self.box_color = QColor(255,255,255)

        self.padding = 10
        self.spacing = 10
        self.font_size = 8

        self.ferdieling: float = 0.5

        self.data = {}

    def set_data(self, data_dict):
        self.data = data_dict
        self.update()

    def update_data(self, data_dict):
        for key, value in data_dict.items():
            if key in self.data:
                self.data[key] = str(value)
        self.update()

    def paintEvent(self, event):

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        ## tlo
        painter.setBrush(self.background_color)
        painter.setPen(QPen(Qt.black, 2))
        painter.drawRect(self.rect().adjusted(1, 1, -1, -1))

        if not self.data:
            return

        ## obliczenie wymiarów
        rows = len(self.data)
        ## Szerokość
        cell_width = (self.width() - (2 * self.padding) - self.spacing)
        ## Wysokość
        cell_height = (self.height() - (2 * self.padding) - ((rows - 1) * self.spacing)) / rows

        cell_width_Left = int((1.0 - self.ferdieling) * cell_width)
        cell_width_Right = int((self.ferdieling ) * cell_width)

        painter.setFont(QFont("Segoe UI", self.font_size, QFont.Bold))

        m = 5

        ## rysowanie wierszy
        for i, (key, value) in enumerate(self.data.items()):
            y_offset = self.padding + i * (cell_height + self.spacing)

            left_rect = QRectF(self.padding, y_offset, cell_width_Left, cell_height)
            right_rect = QRectF(self.padding + cell_width_Left + self.spacing, y_offset, cell_width_Right, cell_height)

            left_rect_area = left_rect.adjusted(m, 0, -m, 0)
            right_rect_area = right_rect.adjusted(m, 0, -m, 0)

            ## rysowanie pól
            painter.setBrush(self.box_color)
            painter.setPen(QPen(Qt.black, 2))
            painter.drawRoundedRect(left_rect, 10, 10)
            painter.drawRoundedRect(right_rect, 10, 10)

            ## rysowanie tekstu
            painter.setPen(Qt.black)
            painter.drawText(left_rect_area, Qt.AlignCenter, str(key)) ## Qt.AlignLeft |
            painter.drawText(right_rect_area, Qt.AlignCenter, str(value)) ##  Qt.AlignRight |