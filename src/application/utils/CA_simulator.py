import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox
)
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import QSize
from PyQt5.QtCore import Qt
from random import randint

colors = {
    0: QColor(32, 32, 32),
    1: QColor(255, 0, 150),
    2: QColor(255, 255, 0),
    3: QColor(0, 0, 255),
    4: QColor(0, 255, 0),
    5: QColor(255, 200, 150),
    6: QColor(0, 100, 0),
    7: QColor(100, 60, 20),
    8: QColor(255, 150, 50),
    9: QColor(130, 0, 255),
    10: QColor(128, 128, 128),
    11: QColor(255, 50, 50),
    12: QColor(150, 0, 70),
    13: QColor(0, 255, 255),
}

# Funkcja do mapowania wartości na kolor tła
def value_to_color(value: int) -> str:
    return colors.get(value, "red")  # >5 → czerwony

import numpy as np

class CounterButton(QPushButton):

    instance = []

    def __init__(self):
        super().__init__(" ")

        CounterButton.instance.append(self)

        self.count = 0
        self.setFixedSize(QSize(30, 80))
        self.setText(" ")
        self.clicked.connect(self.increment)
        self.update_color()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.increment()
        elif event.button() == Qt.RightButton:
            self.decrement()
        # zachowanie standardowego kliknięcia
        # super().mousePressEvent(event)

    def increment(self):
        self.count += 1
        if self.count >= len(colors):
            self.count = 0
        # self.setText(str(self.count))
        self.update_color()

    def decrement(self):
        self.count -= 1
        if self.count <= 0:
            self.count = len(colors)-1
        # self.setText(str(self.count))
        self.update_color()

    def refresh(self):
        # self.setText(str(self.count))
        self.update_color()

    def res(self):
        self.count = 1
        # self.setText(str(self.count))
        self.update_color()

    def rand(self):
        self.count = randint(0, len(colors)-1 )
        # self.setText(str(self.count))
        self.update_color()

    def update_color(self):
        color = value_to_color(self.count)
        # ustawienie tła przycisku przez stylesheet
        self.setStyleSheet(f"background-color: {color.name()}; border: 1px solid black;")

class MainWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Colorful Counters")

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # 9 przycisków w rzędzie
        row_layout = QHBoxLayout()
        self.buttons = []
        for _ in range(9):
            btn = CounterButton()
            self.buttons.append(btn)
            row_layout.addWidget(btn)
        row_layout.setSpacing(0)
        row_layout.setContentsMargins(0,0,0,0)
        main_layout.addLayout(row_layout)


        wq = QWidget( self )
        wq.setFixedSize( 100, 100)
        main_layout.addWidget( wq )

        # Zielony przycisk pod nimi
        self.green_button = QPushButton("Step")
        self.green_button.setFixedSize(QSize(100, 50))
        self.green_button.setStyleSheet("background-color: green; border: 1px solid black;")
        self.green_button.clicked.connect(self.say_hello)
        main_layout.addWidget(self.green_button)

        self.green_button2 = QPushButton("Random")
        self.green_button2.setFixedSize(QSize(100, 50))
        self.green_button2.setStyleSheet("background-color: green; border: 1px solid black;")
        self.green_button2.clicked.connect(lambda: [ ic.rand() for ic in CounterButton.instance] )
        main_layout.addWidget(self.green_button2)

    def say_hello(self):
        try:
            Q_t = np.array( [ inst.count for inst in CounterButton.instance ] )

            V = np.concatenate( [ [-1, -1], Q_t, [-1, -1]])

            T = np.row_stack(  [ V[n:n+5] for n in range(0,9)] )

            U = []
            for trr in T:
                urr =[]
                for t in trr:
                    if t == -1:
                        urr.append( trr[2] )
                    else:
                        urr.append( t )
                U.append( np.array(urr) )
            U = np.array( U )

            E = lambda X, Y: (X if X==Y else 0)
            D = lambda X, Y: (0 if X+Y==0 else (X or Y) )
            C = lambda X, Y: ( X or Y )

            # print("\n\nU",U)
            W = []
            X = []
            Z = []
            Y = []
            for urr in U:
                wrr = []
                xrr = []
                zrr = []
                yrr = []

                wrr.append( E(urr[0], urr[1] ) )
                wrr.append( urr[2] )
                wrr.append( E(urr[3], urr[4] ) )

                xrr.append( E(wrr[0], wrr[1] ) )
                xrr.append( E(wrr[1], wrr[2] ) )

                zrr.append( C(xrr[0], xrr[1] ) )

                yrr.append( D(wrr[0], wrr[2] ) )
                yrr.append( D(wrr[2], wrr[0] ) )

                W.append(wrr)
                X.append(xrr)
                Z.append(zrr)
                Y.append(yrr)

            W = np.array( W )
            X = np.array( X )
            Z = np.array( Z )
            Y = np.array( Y )


            # print("W", W)
            # print("X", X)
            # print("Z", Z)
            # print("Y", Y)

            Q_tp1 = []
            for i, (zrr, yrr) in enumerate( zip(Z, Y)):
                if zrr[0] != 0: Q_tp1.append( zrr[0] )
                else:
                    s = 1 if i < len(Q_t)/2 else 0
                    Q_tp1.append( yrr[s])

            Q_tp1 = np.array(Q_tp1)
            if np.all(Q_t[1:5] == 0):
                Q_tp1[1:5] = 0
            if np.all(Q_t[4:8] == 0):
                Q_tp1[4:8] = 0


            for q, inst in zip(Q_tp1, CounterButton.instance):
                inst.count = q
                inst.refresh()


        except Exception as e:
            print(e)

        # print("\n\n")
        # arr = [0 for _ in range(9)]
        # instc = CounterButton.instance
        # # for i in inst:
        # #     i.increment()
        #
        # vals = [-1, -1] + [ic.count for ic in instc] + [-1, -1]
        #
        # for i in range(2,2+9):
        #
        #     tar =  [ # 0 1 | 2 | 3 4
        #         vals[i] if v==-1 else v
        #         for v in vals[i-2:i+2+1]
        #     ]
        #
        #     L = None
        #     R = None
        #
        #     if tar[0] == tar[1]: L = tar[0]
        #     if tar[3] == tar[4]: R = tar[4]
        #     print(tar[:2], tar[2], tar[-2:])
        #
        #     if tar[2] == L : tar[2]=L
        #     elif tar[2] == R: tar[2]=R
        #     else:
        #         if i <= len(vals)//2:
        #             if L: tar[2]=L
        #             elif R: tar[2]=R
        #             # elif tar[2]==0:
        #             #     if i==2+1: tar[2]=tar[1]
        #             #     elif i==9+2-1: tar[2]=tar[3]
        #             #     else: tar[2] = tar[2]
        #             else: tar[2]=0
        #         else:
        #             if R: tar[2] = R
        #             elif L: tar[2] = L
        #             # elif tar[2]==0:
        #             #     if i==2+1: tar[2]=tar[1]
        #             #     elif i==9+2-1: tar[2]=tar[3]
        #             #     else: tar[2] = tar[2]
        #             else: tar[2]=0
        #
        #     arr[i-2] = tar[2]
        #     print(arr)
        # else:
        #     for a, ic in zip(arr, instc):
        #         ic.count = a
        #         ic.refresh()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWidget()
    w.show()
    sys.exit(app.exec_())
