import pyzed.sl as sl
import cv2

import time

from typing import List
from src.func.special import NPY
import numpy as np

from data.project_values import *


def main():
    zed = sl.Camera()

    # Parametry wejściowe
    init_params = sl.InitParameters()
    init_params.camera_resolution = sl.RESOLUTION.HD720
    init_params.camera_fps = 30

    # WYŁĄCZENIE GŁĘBI - to sprawi, że program ruszy od razu bez optymalizacji AI
    init_params.depth_mode = sl.DEPTH_MODE.NONE

    # Otwórz kamerę
    if zed.open(init_params) != sl.ERROR_CODE.SUCCESS:
        print("Nie udało się otworzyć kamery.")
        return

    image = sl.Mat()
    print("Działa! Naciśnij 'q' aby wyjść.")

    data: List = []

    i = 0
    while True:

        start_time = time.time()

        if zed.grab() == sl.ERROR_CODE.SUCCESS:
            # Pobierz surowy obraz z lewego obiektywu
            zed.retrieve_image(image, sl.VIEW.LEFT)

            # Wyświetl obraz w oknie
            cv2.imshow("ZED Podgląd", image.get_data())

            print("Models")
            time.sleep(0.018)
            time.sleep(0.020)


        end_time = time.time()


        c_time = end_time - start_time

        i += 1

        print(i, c_time)
        data.append(c_time)

        if cv2.waitKey(1) & 0xFF == ord('q') or i > 400:

            DATA_array = np.array(data)

            NPY.save( "CAMERA_TIMER_RECO", DATA_array )

            break

    zed.close()
    cv2.destroyAllWindows()


if __name__ == "__main__" and 1:
    main()

if __name__ == "__main__" and 1:

    import matplotlib.pyplot as plt

    plt.figure(figsize=(14,10))

    dataY = NPY.load( "CAMERA_TIMER_RECO" )

    yMean = np.mean(dataY)

    LOG.print(yMean)

    dataX = np.arange(len(dataY))

    plt.plot(dataX, dataY, marker='o', linestyle='-', color='blue')

    plt.xlim(0, 400)
    plt.ylim(0, 0.15)
    plt.axhline(y=yMean, color='red', linestyle='-', linewidth=3)

    plt.title("ZED frame time recognizion (HD720) and daley 48ms  ", fontsize=20)
    plt.xlabel("Sample", fontsize=12)
    plt.ylabel("Time [ms]", fontsize=12)
    plt.grid(True)

    plt.savefig(os.path.join(PATH.axes_distbt, "test_frame.jpg"), dpi=300)
    # plt.show()
    plt.close()