from PyQt5.QtCore import QThread, pyqtSignal

from sklearn.preprocessing import LabelEncoder
from src.func.special import MODEL_H5, NPY

import numpy as np

class Thread_CentralUnit(QThread):


    def __init__(self):
        super().__init__()

        pass

    def run(self):
        pass

        model = MODEL_H5.load(MODEL_H5.base_name)

        encoder = LabelEncoder()
        encoder.classes_ = NPY.load(NPY.classes, allow_pickle=True)

        while True:

            norm_LParray = np.random.rand(1, 63)

            pred = model.predict( norm_LParray.reshape(1, 63), verbose=0 )

            class_id = np.argmax(pred, axis=1)[0]

            label = encoder.inverse_transform([class_id])[0]

            print(label)

from PyQt5.QtWidgets import QApplication, QWidget
import sys

class MainWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setGeometry(0, 0, 300, 300)

        self.TCU = Thread_CentralUnit()
        self.TCU.start()


if __name__ == '__main__':

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())

