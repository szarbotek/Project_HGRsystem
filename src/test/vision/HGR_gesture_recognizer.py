import cv2
import mediapipe as mp
import pyzed.sl as sl
import numpy as np

from data.project_values import *

def main():

    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    mp_hands = mp.solutions.hands

    BaseOptions = mp.tasks.BaseOptions
    GestureRecognizer = mp.tasks.vision.GestureRecognizer
    GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
    VisionRunningMode = mp.tasks.vision.RunningMode

    options = GestureRecognizerOptions(
        base_options=BaseOptions(model_asset_path=PATH.models+"/gesture_recognizer.task"  ),
        running_mode=VisionRunningMode.IMAGE
    )

    with GestureRecognizer.create_from_options(options) as recognizer:

        pass

        zed = sl.Camera()

        init_params = sl.InitParameters()

        # parametry kamerki, rozdzielczoć, głebia, FPS
        init_params.camera_resolution = sl.RESOLUTION.HD1080
        init_params.depth_mode = sl.DEPTH_MODE.NONE
        init_params.camera_fps = 30

        # kontener na buffor
        image_zed = sl.Mat()

        if zed.open(init_params) != sl.ERROR_CODE.SUCCESS:
            print("ERROR")
            return

        while True:
            if zed.grab() == sl.ERROR_CODE.SUCCESS:

                #przecienisienie buffora z lewej kamerry do mem GPU
                zed.retrieve_image(image_zed, sl.VIEW.LEFT, sl.MEM.GPU)

                # err, left_center = image_zed.get_value( int(image_zed.get_width() / 2), int(image_zed.get_height() / 2) )
                # print("left_image center pixel R:", int(left_center[0]), " G:", int(left_center[1]), " B:", int(left_center[2]))

                #załoadowanie zdjecia z pamieciu gpu do cpy
                image_zed.update_cpu_from_gpu()

                #pobranice zjdecia z pamieci
                frame_bgra = image_zed.get_data()

                frame_bgr = cv2.cvtColor(frame_bgra, cv2.COLOR_BGRA2BGR)
                frame_rgb = cv2.cvtColor(frame_bgra, cv2.COLOR_BGRA2RGB)

                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb )

                results = recognizer.recognize( mp_image )

                if results.hand_landmarks:

                    print( results.gestures[0] )

                    for hand_landmarks_list in results.hand_landmarks:

                        # TERAZ UWAGA: hand_landmarks_list to lista obiektów NormalizedLandmark
                        # Nie musisz pisać .landmark, bo to już są te punkty
                        for idx, landmark in enumerate(hand_landmarks_list):

                            h, w, c = frame_bgr.shape
                            cx, cy = int(landmark.x * w), int(landmark.y * h)

                            cv2.circle(frame_bgr, (cx, cy), 3, (0, 0, 255), -1)

                cv2.imshow("ZED Gesture Recognition", cv2.flip(frame_bgr, 1 ))

                # image = None
                # results = hands.process( image )

            if cv2.waitKey(5) & 0xFF == 27:
                zed.close()
                break

main()