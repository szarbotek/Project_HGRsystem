import pyzed.sl as sl
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np


def main():
    zed = sl.Camera()
    init_params = sl.InitParameters()
    init_params.camera_resolution = sl.RESOLUTION.HD720
    init_params.depth_mode = sl.DEPTH_MODE.NONE

    if zed.open(init_params) != sl.ERROR_CODE.SUCCESS:
        print("❌ Nie udało się otworzyć kamery ZED")
        return

    image_zed = sl.Mat()

    print("✅ Start. Naciśnij Q aby zakończyć.")

    # =========================
    # 3. Główna pętla
    # =========================
    while True:
        if zed.grab() == sl.ERROR_CODE.SUCCESS:
            zed.retrieve_image(image_zed, sl.VIEW.LEFT)

            # ZED -> numpy (RGBA)
            frame_rgba = image_zed.get_data()

            # RGBA -> BGR (OpenCV)
            frame_bgr = cv2.cvtColor(frame_rgba, cv2.COLOR_RGBA2BGR)

            # BGR -> RGB (MediaPipe)
            frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            frame_rgb = np.ascontiguousarray(frame_rgb, dtype=np.uint8)

            # Wyświetlanie (BGR!)
            cv2.imshow("ZED Gesture Recognition", frame_bgr)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    zed.close()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
