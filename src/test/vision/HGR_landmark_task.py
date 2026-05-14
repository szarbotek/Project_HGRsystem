import cv2
import time
import mediapipe as mp
from mediapipe.tasks import python as mp_python
import pyzed.sl as sl
import numpy as np

from data.project_values import PATH
from src.func.analyzing_tool import select_higher_gesture, get_landmark_site, landmark2array, normalization

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

def main():
    # ===============================
    # Opcje MediaPipe HandLandmarker
    # ===============================
    options = mp_python.vision.HandLandmarkerOptions(
        base_options=mp_python.BaseOptions(
            model_asset_path=PATH.hand_landmark,
            delegate=mp_python.BaseOptions.Delegate.CPU,  # CPU zgodnie z życzeniem
        ),
        num_hands=2,  # zostawiamy 2 dłonie
        running_mode=mp.tasks.vision.RunningMode.VIDEO,  # zmiana pod wideo
        min_hand_presence_confidence=0.7,
        min_hand_detection_confidence=0.7,
        min_tracking_confidence=0.8,
    )

    with mp_python.vision.HandLandmarker.create_from_options(options) as recognizer:
        # ===============================
        # Inicjalizacja kamery ZED
        # ===============================
        zed = sl.Camera()
        init_params = sl.InitParameters()
        init_params.camera_resolution = sl.RESOLUTION.HD720
        init_params.depth_mode = sl.DEPTH_MODE.NONE
        init_params.camera_fps = 30

        image_zed = sl.Mat()

        if zed.open(init_params) != sl.ERROR_CODE.SUCCESS:
            print("ERROR: Nie udało się otworzyć kamery")
            return

        while True:
            if zed.grab() == sl.ERROR_CODE.SUCCESS:
                # Pobranie obrazu z GPU
                zed.retrieve_image(image_zed, sl.VIEW.LEFT, sl.MEM.GPU)
                image_zed.update_cpu_from_gpu()
                frame_bgra = image_zed.get_data()

                # Konwersja BGRA -> RGB i BGR
                frame_acc_rgb = cv2.cvtColor(frame_bgra, cv2.COLOR_BGRA2RGB)
                frame_acc_bgr = cv2.cvtColor(frame_bgra, cv2.COLOR_BGRA2BGR)

                # Obiekt MediaPipe Image
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_acc_rgb)

                # ===============================
                # DETEKCJA DŁONI POD VIDEO
                # ===============================
                timestamp_ms = int(time.time() * 1000)  # potrzebne w trybie VIDEO
                result = recognizer.detect_for_video(mp_image, timestamp_ms)

                # Debug: wypisz wynik
                # print(result)

                # ===============================
                # Rysowanie landmarków
                # ===============================
                if result.hand_landmarks:
                    for hand_landmarks_list in result.hand_landmarks:
                        for idx, landmark in enumerate(hand_landmarks_list):
                            h, w, c = frame_acc_bgr.shape
                            cx, cy = int(landmark.x * w), int(landmark.y * h)
                            cv2.circle(frame_acc_bgr, (cx, cy), 3, (0, 0, 255), -1)

                # ===============================
                # Wyświetlenie obrazu z flipem
                # ===============================
                cv2.imshow("ZED Gesture Recognition", cv2.flip(frame_acc_bgr, 1))

            # ESC do wyjścia
            if cv2.waitKey(5) & 0xFF == 27:
                zed.close()
                break

if __name__ == "__main__":
    main()
