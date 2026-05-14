from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import Qt

import numpy as np

from typing import List

class FlowChart(QWidget):

    gesture_colors = {
        "call": QColor(255, 0, 150),
        "dislike": QColor(100, 60, 20),
        "fist": QColor(0, 0, 255),
        "grip": QColor(0, 255, 0),
        "like": QColor(255, 200, 150),
        "little_finger": QColor(0, 100, 0),
        "one": QColor(255, 255, 0),
        "peace": QColor(255, 150, 50),
        "rock": QColor(130, 0, 255),
        "stop": QColor(128, 128, 128),
        "three": QColor(255, 50, 50),
        "three3": QColor(150, 0, 70),
        "thumb_index": QColor(0, 255, 255),
        "None": QColor(32, 32, 32),
        None: QColor(0, 0, 0)
    }


    def __init__(self, parent=None, max_segments=3, segment_per_box=1):
        super().__init__(parent=parent)

        ## przypisanie instancji do aktywnych bytów

        self.max_segments = max_segments
        self.segment_per_box = segment_per_box
        self.max_boxs = self.max_segments * self.segment_per_box

        self.data: List[str] = []

        self.time_refresh_ms = 100
        self.time_next_refresh_ms = 0

    def new_data(self, dataset: List[str]):
        assert isinstance(dataset, List), TypeError(self.__class__.__name__)
        assert all(isinstance(_, str) for _ in dataset), TypeError(self.__class__.__name__)

        self.data = dataset

    def refresh(self, time_interval_ms:int):
        self.time_next_refresh_ms += time_interval_ms

        if self.time_next_refresh_ms >= self.time_refresh_ms:
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)  # Opcjonalnie dla lepszej jakości

        width = self.width()
        height = self.height()

        # Obliczamy dokładną szerokość jednego paska jako float, by uniknąć luk
        box_width = width / self.max_boxs
        d = 2  # margines pionowy

        # Rysowanie tła (czarne)
        painter.setBrush(FlowChart.gesture_colors["None"])
        painter.drawRect(0, 0, width, height)

        # Rysujemy od najstarszych (lewa) do najnowszych (prawa)
        # Zakładając, że self.data przechowuje maksymalnie self.max_boxs elementów
        for i, label in enumerate(self.data):
            color = FlowChart.gesture_colors.get(label, FlowChart.gesture_colors["None"])
            painter.setBrush(color)
            painter.setPen(Qt.NoPen)  # Usuwamy obramowanie, by paski przylegały do siebie

            # Obliczamy pozycję X
            x_pos = int(i * box_width)
            # Szerokość paska (używamy int, ale dbamy o wypełnienie luki do następnego x)
            current_w = width - (int((i + 1) * box_width) - x_pos)

            painter.drawRect(x_pos, d, current_w, height - 2 * d)