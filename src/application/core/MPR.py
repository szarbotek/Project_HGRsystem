import numpy as np

import traceback

import mediapipe as mp
from mediapipe.tasks import python as mp_python


from PyQt5.QtCore import QThread, pyqtSignal

from data.project_values import LOG, FALG_NORMALIZATION, PATH
from src.application.utils.structure import CircularBuffer

import time

from numpy.typing import NDArray
from typing import Tuple, Dict, Any

class MediapipeRecognizer(QThread):
    """
        Klasa MediapipeRecognizer(QThread):

        Odpowiada za detekcje landmarku na podstawie ramki

    """

    SIGNAL_A002_2GUI = pyqtSignal(int, object) ## przesył landmarku
    SIGNAL_A003_2UIC = pyqtSignal(int, object) ## przesył landmarku

    def SIGNAL_A001_4CAM(self, *args):
        try:
            ## sprawdzenie struktury przesyłu danych
            assert len(args) == 2, IndexError
            ## zapsianie danych klatki do Wigetu odpowiedzialnego za wyswietlanie
            ts = args[0]
            frame = args[1]
            self.data_frame_2_recognition.put((ts, frame))
        except Exception as e:
            LOG.print(f"<ERR> SIGNAL_A001_4CAM: {e}, {args}")


    ### ================================================================================================================

    def __init__(self):
        super().__init__()
        LOG.print(f"MPR: [INIT] initialize thread ")

        ## zdeniowanie opcji modelu rozpoznawania landmarków
        ## https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker?hl=pl
        self.options = mp_python.vision.HandLandmarkerOptions(
            base_options=mp_python.BaseOptions(
                model_asset_path=PATH.hand_landmark, # ścierzka do modelu
                delegate=mp_python.BaseOptions.Delegate.CPU,
            ),
            num_hands=2,
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
            min_hand_presence_confidence=0.5,
            min_hand_detection_confidence=0.5,
            min_tracking_confidence=0.7,
        )

        self.data_frame_2_recognition: CircularBuffer = CircularBuffer(60)

    def run(self):
        try:
            LOG.print(f"MPR: [PROC] Activate MediapipeRecognizer")
            last_timestamp = 0

            with mp_python.vision.HandLandmarker.create_from_options(self.options) as recognizer:
                LOG.print(f"MPR: .[INFO] Model: hand_landmarker.task, opened!")

                timestamp_recognizer: int = 0

                while True:

                    if len(self.data_frame_2_recognition)  > 0:
                        start_time = time.time()
                        ts, frame_RGB = self.data_frame_2_recognition.throw()

                        ## przekształcanei zdjecia do formatu MP
                        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_RGB)

                        ## uaktualnienie timestamp
                        timestamp_recognizer += ts

                        ## detekcja dłoni
                        result = recognizer.detect_for_video(mp_image, timestamp_recognizer)

                        ## przypisanie landmarku do ręki
                        data_landmarks: Dict[str, Any] = {
                            "Right": None,
                            "Left": None,
                        }

                        ## przypisanie landmarków do odpowiednich dłoni
                        for index, (lk, hd) in enumerate( zip(result.hand_landmarks, result.handedness) ):
                            side = hd[0].category_name
                            data_landmarks[side] = lk

                        proc_time_ms = int( abs(time.time() - start_time) * 1000)


                        ## przesył landmarku
                        self.SIGNAL_A002_2GUI.emit(
                            ts-proc_time_ms, data_landmarks.copy()
                        )
                        self.SIGNAL_A003_2UIC.emit(
                            ts-proc_time_ms, data_landmarks.copy()
                        )

                        """
                            Ponieważ klatki są dostarczane co ok. 33–44 ms, a próbkowanie w modelu odbywa się co 100 ms, 
                            model potrzebuje co najmniej jednej próbki.  Jeśli zostaną usunięte dwie dodatkowe próbki, 
                            to z trzech możliwych próbek do detekcji pozostaje tylko jedna. W efekcie skraca się czas
                            rozpoznawania, a tym samym poprawia się synchronizacja z ekranem oraz zmniejsza złożoność 
                            obliczeniowa.
                        """
                        if len(self.data_frame_2_recognition) >= 3:
                            self.data_frame_2_recognition.throw()
                            self.data_frame_2_recognition.throw()
                    ##endif
                ##while

        except Exception as e:
            LOG.print(f"<ERR> Thread MediapipeRecognizer cannot be run: {e}")
            LOG.print(traceback.format_exc())

        LOG.print(f"\n[THREAD] Activate MediapipeRecognizer")
        self.quit()
