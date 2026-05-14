import traceback

from data.project_values import LOG
from src.application.utils.structure import CircularBuffer

from PyQt5.QtWidgets import  QLabel
from PyQt5.QtGui import QImage, QPixmap, QColor, QPainter, QPen
from PyQt5.QtCore import Qt

from numpy.typing import NDArray
from typing import Dict, Any, List, Tuple

from application.ui.components.jumping_machine import JumpingMachine

class JpCameraScreen(QLabel, JumpingMachine):
    def __init__(self, parent=None):
        super().__init__( parent=parent, parentJP=parent, instanceJP=self)

        self.setParent(parent)
        self.setText("Brak danych")

        ## kolejka na klatki, landmarki odbierane od kamery i przetwarzane
        self.frame_data: CircularBuffer = CircularBuffer(60)
        self.landmarks_data: CircularBuffer = CircularBuffer(60)

        ## timestamp
        self.time_next_frame:int = 0
        self.time_next_landmarks:int = 0

        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("color: white; background-color: black;")

        self.active_landmarks: Dict[str, list[Tuple[float, float]]] = {
            "Right": [],
            "Left": [],
        }

        ## falgi
        self.FLAG_draw_landmarks = True

    def padding(self, value: int):
        pos = self.pos()
        x,y = pos.x(), pos.y()
        self.setGeometry(x + value, y + value, self.width() - 2 * value, self.height() - 2 * value)

    def new_frame(self, timestamp_ms:int, frame: List[NDArray]):
        self.frame_data.put( (timestamp_ms, frame) )

    def new_landmarks(self, timestamp_ms:int, landmarks: Dict[str, Any]):
        self.landmarks_data.put( (timestamp_ms, landmarks) )

    def refresh(self, time_intervl_ms: int):
        try:
            self.time_next_frame += time_intervl_ms
            self.time_next_landmarks += time_intervl_ms

            if len(self.landmarks_data) > 0:
                timestamp, _ = self.landmarks_data.last
                ## jeśli licznik czasowy przekroczy timestamp rysowane zostają landmarki
                if self.time_next_landmarks >= timestamp:
                    self.time_next_landmarks -= timestamp
                    ## pozbycie się z kolejki najstarzego elementu
                    _, landmarks = self.landmarks_data.throw()
                    ## rysowanie ramki
                    self.update_landmarks(landmarks)

            if len(self.frame_data) > 0:
                timestamp, _ = self.frame_data.last
                ## jeśli licznik czasowy przekroczy timestamp rysowana zostaje klatka
                if self.time_next_frame >=  timestamp:
                    self.time_next_frame -= timestamp
                    ## pozbycie się z kolejki najstarzego elementu
                    _, frame = self.frame_data.throw()
                    ## rysowanie ramki
                    self.update_screen(frame)

        except Exception as e:
            LOG.print(f"<ERR> JpCameraScreen refresh : {e}")
            LOG.print(traceback.format_exc())

    def update_screen(self, frame: NDArray):
        try:
            ## pobranie wymiarów obrazu na podstawie ramki
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            ## przełożenie tablicy ramki na obraz wiget'u
            qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimg)
            ## przeskalowanie ramki do wymiarów widget'u
            scaled_pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatio)

            if self.FLAG_draw_landmarks:
                ## wywołanie instancji pisanka
                painter = QPainter(scaled_pixmap)

                # konfiguracja pisaka
                pen = QPen(QColor('red'))
                pen.setWidth(5)
                painter.setPen(pen)

                ## rysowanie punktów
                for lk in self.active_landmarks.values():
                    for p in lk:
                        DX, DY = p
                        painter.drawPoint(DX, DY)
                ## zamknięcie pisaka
                painter.end()

            self.setPixmap(scaled_pixmap)
        except Exception as e:
            LOG.print(f"<ERR> JpCameraScreen update screen: {e}, {frame}")
            LOG.print(traceback.format_exc())

    def update_landmarks(self, landmarks: Dict[str, Any]):
        try:
            ## rozmiar mapy pixeli
            sw = self.width()
            sh = self.height()

            for st, lk in landmarks.items():
                ## pominięcie ręki bez dostepnych danych
                if lk is None:
                    self.active_landmarks[st] = []
                    continue
                else:
                    ## przeskalowanie punktów landmarku względem rozmiaru pixmap
                    self.active_landmarks[st] = [
                        (
                            int(sw * p.x),
                            int(sh * p.y),
                        )
                        for p in lk
                    ]

        except Exception as e:
            LOG.print(f"<ERR> JpCameraScreen update landmarks: {e}, {landmarks}")


    # def draw_screen(self, timestamp: int, frame: NDArray, landmarks ):
    #     """
    #         Odścwierzanie ekranu obieranego z kamery
    #     """
    #     try:
    #
    #         h, w, ch = frame.shape # przykładowe dane 720 1280 3
    #         bytes_per_line = ch * w
    #         qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
    #
    #         pixmap = QPixmap.fromImage(qimg)
    #         scaled_pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatio)
    #
    #         if self.FLAG_DRAW_LANDMARKS:
    #             self.draw_landmark( scaled_pixmap, landmarks )
    #
    #         self.setPixmap(scaled_pixmap)
    #
    #     except Exception as e:
    #         print(e)
    #
    # def draw_landmark(self, pixmap, landmarks: Dict[str, Any]  ):
    #     """
    #         Funlcja rysuje ladmarka na ekranie w GUI
    #     """
    #
    #     for lk in landmarks.values():
    #         if lk is None:
    #             continue
    #         else:
    #             # wywołanie instancji pisanka po płutnie
    #             painter = QPainter(pixmap)
    #
    #             # konfiguracja pisaka
    #             pen = QPen(QColor('red'))
    #             pen.setWidth(5)
    #             painter.setPen(pen)
    #
    #             sw = pixmap.width()
    #             sh = pixmap.height()
    #
    #             for p in lk:
    #                 DX = int(sw * p.x)
    #                 DY = int(sh * p.y)
    #
    #                 painter.drawPoint(DX, DY)
    #
    #             painter.end()
