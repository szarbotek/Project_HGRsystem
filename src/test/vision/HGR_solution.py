import cv2
import mediapipe as mp
import pyzed.sl as sl
import numpy as np

from data.project_values import *
from src.func.analyzing_tool import select_higher_gesture, get_landmark_site, landmark2array, normalization

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

def main():
    with mp_hands.Hands(
            model_complexity=0,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5) as hands:

        zed = sl.Camera()

        init_params = sl.InitParameters()
        init_params.camera_resolution = sl.RESOLUTION.HD720
        init_params.depth_mode = sl.DEPTH_MODE.NONE
        init_params.camera_fps = 30

        image_zed = sl.Mat()

        if zed.open(init_params) != sl.ERROR_CODE.SUCCESS:
            print("ERROR")
            return

        while True:
            if zed.grab() == sl.ERROR_CODE.SUCCESS:
                zed.retrieve_image(image_zed, sl.VIEW.LEFT, sl.MEM.GPU)

                # err, left_center = image_zed.get_value( int(image_zed.get_width() / 2), int(image_zed.get_height() / 2) )
                # print("left_image center pixel R:", int(left_center[0]), " G:", int(left_center[1]), " B:", int(left_center[2]))

                image_zed.update_cpu_from_gpu()

                frame_rgba = image_zed.get_data()

                frame_bgr = cv2.cvtColor(frame_rgba, cv2.COLOR_RGBA2BGR)
                frame_rgb = cv2.cvtColor(frame_rgba, cv2.COLOR_RGBA2RGB)


                result = hands.process( frame_bgr )

                if result.multi_hand_landmarks:
                    for hand_landmarks in result.multi_hand_landmarks:
                        mp_drawing.draw_landmarks(
                            frame_rgb,
                            hand_landmarks,
                            mp_hands.HAND_CONNECTIONS,
                            mp_drawing_styles.get_default_hand_landmarks_style(),
                            mp_drawing_styles.get_default_hand_connections_style(),
                        )


                cv2.imshow("ZED Gesture Recognition", cv2.flip(frame_rgb, 1 ))

            if cv2.waitKey(5) & 0xFF == 27:
                zed.close()
                break

main()
