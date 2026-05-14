import numpy as np

from data.project_values import *

import mediapipe as mp
from mediapipe.tasks import python as mp_python

import pyzed.sl as sl

from PyQt5.QtCore import QThread, pyqtSignal, QRect
from PyQt5.QtWidgets import QApplication

from numpy.typing import NDArray
import cv2

from typing import Dict, Any

"""
    Wątek kamerki
"""

from src.func.analyzing_tool import landmark2array, normalization,  get_landmark_site

class CameraThread(QThread):
    """
        Watek do wysyłania obrazu zczytanego z kamery

        Obraz jest wysyłany do:
            >> jednostki rozpoznawania
            >> GUI

    """

    singal_frame = pyqtSignal(int, object)
    singal_landmarks = pyqtSignal(int, object)

    signal_site_hand = pyqtSignal(str )

    def __init__(self):
        super().__init__()

        base_options = mp_python.BaseOptions(
            model_asset_path=PATH.hand_landmark,
            delegate=mp_python.BaseOptions.Delegate.CPU  # GPU
        )

        # https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker?hl=pl
        self.options = mp_python.vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=2,
            running_mode=mp.tasks.vision.RunningMode.IMAGE,
            min_hand_presence_confidence=0.15,
            min_hand_detection_confidence=0.15,
            min_tracking_confidence=0.6,
        )


        self.zed = sl.Camera()

        # inicjacja paramterów kamery
        self.init_params = sl.InitParameters()

        self.init_params.camera_resolution = sl.RESOLUTION.HD720 # 1280x720
        self.init_params.depth_mode = sl.DEPTH_MODE.NONE
        self.init_params.camera_fps = 30

        #buffor pamięci przechowujący matryce obrazową
        self.image_array = sl.Mat()

        # ustawienie dostępu do kamer
        self.cam_choice = {
            "Right": sl.VIEW.RIGHT,
            "Left": sl.VIEW.LEFT,
        }
        # aktywna strona odczytywania
        self.active_cam = "Right"

        if self.zed.open(self.init_params) != sl.ERROR_CODE.SUCCESS:
            raise Exception("<ERR> Camera ZED cannot be opened.")

        self.FLAG_RUN = True

    def run(self):

        i = 0
        LOG.print(f"\n[PROC] Activate process of grabbing image from ZED")

        with mp_python.vision.HandLandmarker.create_from_options(self.options) as recognizer:

            LOG.print(f".[INFO] Model opened!")

            while self.FLAG_RUN:

                i += 1
                if self.zed.grab() == sl.ERROR_CODE.SUCCESS:

                    # pobranie obrazu z lewej kamery
                    self.zed.retrieve_image(self.image_array, self.cam_choice[self.active_cam], sl.MEM.GPU)
                    # załadowanie obrazu z pamieciu GPU
                    self.image_array.update_cpu_from_gpu()

                    timestamp_ns = self.zed.get_timestamp(sl.TIME_REFERENCE.IMAGE).get_nanoseconds()
                    timestamp_ms = int(timestamp_ns // 1_000_000)

                    # odczytanie buffora
                    frame_bgra: NDArray = self.image_array.get_data()


                    # eliminacja kanału alfa
                    frame_rgb = cv2.cvtColor(frame_bgra, cv2.COLOR_RGBA2BGR)
                    frame_bgr = cv2.cvtColor(frame_bgra, cv2.COLOR_RGBA2RGB)

                    # przekształcanei zdjecia do formatu MP
                    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)


                    # detekcja dłoni
                    result = recognizer.detect(mp_image)

                    if len(result.hand_landmarks) == 2:
                        site1, site2 = result.handedness[0][0].category_name, result.handedness[1][0].category_name

                        # wykryto prawą i lewą rękę
                        if site1 != site2:

                            if site1 == "Right":
                                data: Dict[str, Any] ={
                                    "Right": result.hand_landmarks[0],
                                    "Left": result.hand_landmarks[1],
                                }
                            else:
                                data: Dict[str, Any] = {
                                    "Right": result.hand_landmarks[1],
                                    "Left": result.hand_landmarks[0],
                                }

                            self.singal_landmarks.emit( timestamp_ms, data )


                    self.singal_frame.emit(timestamp_ms, frame_rgb.copy() )

        LOG.print(f"\n[ENDPROC]  Desactivate process of grabbing image from ZED")

        self.zed.close()

    def changeSite(self, site: str):
        if site in self.cam_choice.keys():
            self.active_cam = site

    def finished(self):
        self.FLAG_RUN = False


class CentralUnit(QThread):

    def run(self):

        while True:
            pass

from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap, QPalette, QColor, QPainter, QPen
from PyQt5.QtWidgets import QPushButton

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class MainWindow(QWidget):

    signal_site_hand = pyqtSignal(str)


    def __init__(self):
        super().__init__()

        self.setGeometry(0, 0, 1200, 600)

        self.camera_screen = QLabel("Brak danych", self)
        self.camera_screen.setGeometry(0, 50, 640, 360)

        self.setWindowTitle("Informacja z wątku")

        self.CT = CameraThread()
        self.CT.singal_frame.connect(self.update_image)
        self.CT.singal_landmarks.connect(self.update_landmarks)

        self.signal_site_hand.connect( self.CT.changeSite )

        self.CT.start()

        self.FLAG_LANDMARK = False
        self.landmarks = None
        self.timestamp_ms = None

        # wykres
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setParent(self)
        self.canvas.setGeometry(QRect(640, 0, 300, 300))
        self.ax = self.figure.add_axes([0.1, 0.1, 0.8, 0.8])
        self.canvas.draw()


        self.QPushButton = QPushButton(self )
        self.QPushButton.setGeometry(QRect(0, 0, 100, 50))
        self.QPushButton.clicked.connect( self.toggle_flag  )

        self.ButtonRight = QPushButton(self)
        self.ButtonRight.setGeometry(QRect(100, 0, 50, 50))
        self.ButtonRight.clicked.connect( lambda: self.signal_site_hand.emit( "Right" ) )

        self.ButtonRight = QPushButton(self)
        self.ButtonRight.setGeometry(QRect(150, 0, 50, 50))
        self.ButtonRight.clicked.connect( lambda: self.signal_site_hand.emit( "Left" ) )


    def toggle_flag(self):
        self.FLAG_LANDMARK = not self.FLAG_LANDMARK

        color = "red" if self.FLAG_LANDMARK else "green"

        self.QPushButton.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                }}
                QPushButton:hover {{
                    background-color: darkred if self.FLAG_LANDMARK else darkgreen;
                }}
            """)

    def update_landmarks(self, timestamp_ms: int, data: Dict[str, Any] ):
        self.landmarks = data.values()
        self.timestamp_ms = timestamp_ms

        try:
            landmarkR, sideR = data["Right"], "Right"

            LParray = landmark2array(landmarkR)

            normLParray = normalization(LParray, sideR, **FALG_NORMALIZATION)

            normLParray = normLParray.reshape(-1,63)

            x = normLParray[0, 0:-1:3]
            y = normLParray[0, 1:-1:3]

            self.ax.clear()
            self.ax.scatter(x, y,  c=range(21), cmap='rainbow', s=15)
            self.ax.grid(True)

            self.ax.set_xlim(-2, 2)
            self.ax.set_ylim(-2, 2)

            self.ax.invert_yaxis()

            # self.ax.relim()
            # self.ax.autoscale_view()
            self.canvas.draw_idle()
            # ax = self.figure.add_axes([0.1, 0.1, 0.8, 0.8])
            # ax.plot(x, y)
            # ax.grid(True)

        except Exception as e:
            LOG.print(f"<ERR> Analyze problem: {e}")


    def update_image(self, timestamp_ms: int,  frame: np.ndarray):
        """
            funkcja uaktualnia zdjęcia w GUI prz czym musi buyć spełniony warunek gdzie klatka zgadza się z landmarkiem


        """

        # uzupełanine camera screen
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)

        scaled_pixmap = pixmap.scaled(self.camera_screen.size(), Qt.KeepAspectRatio)

        # dorysowawywanie landmarku ON/OFF
        if self.timestamp_ms==timestamp_ms and self.FLAG_LANDMARK and self.landmarks is not None: #

            # wywołanie instancji pisanka po płutnie
            painter = QPainter(scaled_pixmap)

            # konfiguracja pisaka
            pen = QPen(QColor('red'))
            pen.setWidth(5)
            painter.setPen(pen)

            sw = scaled_pixmap.width()
            sh = scaled_pixmap.height()

            for lm in self.landmarks:
                for p in lm:
                    DX = int(sw * p.x)
                    DY = int(sh * p.y)

                    painter.drawPoint( DX, DY)

            painter.end()

            self.landmarks = None

        self.camera_screen.setPixmap(scaled_pixmap)

if __name__ == '__main__':

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())