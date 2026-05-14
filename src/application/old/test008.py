from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import Qt

import time

class AAA(QPushButton):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)

        self._flag = False   # False = released, True = pressed

        self.setAttribute(Qt.WA_Hover, True)

        self.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: 1px solid #388E3C;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: red;
            }
            QPushButton:pressed {
                background-color: #FF9800;
            }
        """)

    def simulate(self, pressed: bool):
        """
            pressed=True  -> symuluj wciśnięcie
            pressed=False -> symuluj zwolnienie
        """
        if pressed == self._flag:
            return  # brak zmiany stanu

        self._flag = pressed
        self.setDown(pressed)

        if pressed:
            self.pressed.emit()
        else:
            self.released.emit()

    # opcjonalnie: toggle jednym wywołaniem
    def toggle(self):
        self.simulate(not self._flag)

    def sim_click(self):
        # self._pressed = True
        # self.setDown(True)
        # self.pressed.emit()

        # self._pressed = False
        # self.setDown(False)
        # self.released.emit()
        self._pressed = True
        self.setDown(True)
        self.pressed.emit()
        time.sleep(0.5)
        self._pressed = False
        self.setDown(False)
        self.released.emit()
        self.clicked.emit()

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        # SYMULOWANY PRZYCISK
        self.button_target = AAA("Docelowy")

        self.button_target.pressed.connect( lambda: print("AAA pressed") )
        self.button_target.released.connect( lambda: print("AAA released") )
        self.button_target.clicked.connect( lambda: print("AAA clicked") )

        # ZWYKŁY PRZYCISK STERUJĄCY
        controller = QPushButton("Steruj AAA")

        controller.clicked.connect(
            self.button_target.sim_click
        )

        self.button_target.pressed.emit()

        layout.addWidget(self.button_target)
        layout.addWidget(controller)


app = QApplication([])
w = MyWindow()
w.show()
app.exec_()
