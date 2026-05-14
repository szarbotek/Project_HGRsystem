"""
    Wątek kamery odpowiada za przehwytywanie obrazu z kamery i przesyłaniu go do do GUI.
    Do wątku kamery został przydzielony hand_lanmdark racognizer, który odciąża pozostałe wątki
    i odpowiadaza wykrywanie dłoni w obszarze pracy kamery. Informacja o landmarkach przesyłana jest zaróbwno do GUI
    w celu ich wrysowania jak i przesłana zostaje informacja do głównej jednoski UIC.

"""

import cv2

from PyQt5.QtCore import QThread, pyqtSignal

from data.project_values import *

import pyzed.sl as sl
import time

from numpy.typing import NDArray
from typing import Tuple, Dict


class ZED:
    """
        Instancja Kmaery Zed z parametrami:
            30 fps, no depht_mode, HD720

    """
    def __init__(self):
        super().__init__()

        ## instancja kamery
        self.cam = sl.Camera()

        ## inicjacja parametrów kamery
        self.init_params = sl.InitParameters()
        self.init_params.camera_resolution = sl.RESOLUTION.HD720
        self.init_params.depth_mode = sl.DEPTH_MODE.NONE
        self.init_params.camera_fps = 30

        ## aktywna strona odczytywania
        self.choice_objective = {
            "Right": sl.VIEW.RIGHT,
            "Left": sl.VIEW.LEFT,
        }
        self.active_cam = "Right"

        ## buffer pamięci przechowujący matryce obrazową
        self.image_array = sl.Mat()

        if self.cam.open(self.init_params) != sl.ERROR_CODE.SUCCESS:
            raise Exception("<ERR:ZED> Camera ZED cannot be opened.")


    def get_image(self) -> Tuple[NDArray|None, int|None]:
        """
            Metoda zwraca frame w formacie RGB, oraz timestamp w ms

            :return frame_rgb: RGB frame
            :return timestamp_ms: timestamp ms
        """

        # wczytanie obrazu z klatki, jęsli kod jest opoprwany zdjęcie zostanie pobrane
        if self.cam.grab() == sl.ERROR_CODE.SUCCESS:
            # pobranie obrazu z lewej kamery
            self.cam.retrieve_image(self.image_array, self.choice_objective[self.active_cam], sl.MEM.CPU)

            # załadowanie obrazu z pamieciu GPU
            # self.image_array.update_cpu_from_gpu()

            # czas pobrania
            timestamp_ns = self.cam.get_timestamp(sl.TIME_REFERENCE.IMAGE).get_nanoseconds()
            timestamp_ms = int(timestamp_ns // 1_000_000)

            # odczytanie buffora
            frame_bgra: NDArray = self.image_array.get_data()

            frame_rgb = cv2.cvtColor(frame_bgra, cv2.COLOR_BGRA2RGB)
            # frame_bgr = cv2.cvtColor(frame_bgra, cv2.COLOR_BGRA2RGB)

            return frame_rgb, timestamp_ms
        else:
            return None, None

    def swap_objective(self, site):
        if site in self.choice_objective.keys():
            self.active_cam = site

class CameraThread(QThread):
    """
        Klasa CameraThread(QThread):

        Opoiwada za rozsyłąnie ramek (frame) dla GUI oraz MPR

    """
    SIGNAL_A000_2GUI: pyqtSignal = pyqtSignal(int, object) ## przesyłanie ramki
    SIGNAL_A001_2MPR: pyqtSignal = pyqtSignal(int, object) ## przesyałanie ramki


    def SIGNAL_Axxx_4GUI(self, *args): ## obieranie falgi zmiany kamery
        self.swap_zed_camera(*args)

    ## =================================================================================================================

    def swap_zed_camera(self, site):
        self.camera_obiect.swap_objective(site)

    def __init__(self):
        super().__init__()
        LOG.print(f"CAM: [INIT] initialize thread ")

        ## inicjacja kamery
        self.camera_obiect: ZED = ZED()
        LOG.print(f"CAM: [INFO] Creat ZED instance")

    def run(self):
        LOG.print(f"CAM: [PROC] Activate process of grabbing image from ZED")
        last_timestamp = 0

        try:
            while True:
                start_time = time.time()

                frame_rgb = None

                if isinstance(self.camera_obiect, ZED):
                    frame_rgb, _ = self.camera_obiect.get_image()
                else:
                    continue

                ## brak obrazu do przetworzenia
                if frame_rgb is None: continue

                ## czas wyznaczania ramki
                timestamp_ms =  int(
                    abs(
                        ( start_time -  time.time() ) * 1000
                    )
                )

                ## przesył ramek
                self.SIGNAL_A000_2GUI.emit(
                    timestamp_ms, frame_rgb.copy()
                )
                self.SIGNAL_A001_2MPR.emit(
                    timestamp_ms, frame_rgb.copy()
                )

        except Exception as e:
            LOG.print(f"<ERR> Thread cannot be run: {e}")
            self.quit()

        LOG.print(f"\n[ENDPROC]  Desactivate process of grabbing image from ZED")
        self.camera_obiect.close()


if __name__ == '__main__':

    z = ZED()
    img, _ = z.get_image()

    frame_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    cv2.imshow("img", frame_bgr)
    cv2.waitKey(0)