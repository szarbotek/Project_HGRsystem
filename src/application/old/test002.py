import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton

from PyQt5.QtGui import QPainter, QColor, QBrush, QPen
from PyQt5.QtCore import Qt


class Frame:
    def __init__(self, border_thickness=1): #, width=0, height=0, border_thickness=1
        self.border_thickness = border_thickness


    def draw_frame(self):
        print("BBB", self.width(), self.height() )

        painter = QPainter(self)

        painter.setBrush(Qt.NoBrush)

        # pen = QPen(QColor("black"), 5, Qt.SolidLine)
        pen = QPen( QColor(0,0,0), 10, Qt.SolidLine)
        painter.setPen(pen)

        wbt = int(self.border_thickness/2)
        hbt = int(self.border_thickness/2)

        W = int(self.width())-2*wbt
        H = int(self.height())-2*hbt

        painter.drawRect(wbt, hbt, W, H)

        # if name == "setGeometry" and callable(attr):
        #     def new_setGeometry(*args, **kwargs):
        #         x, y, h, w, *_ = args
        #
        #         print(x, y, h, w, *_)
        #         x += int(self.border_thickness)
        #         y += int(self.border_thickness)
        #         h -= int(2*self.border_thickness)
        #         w -= int(2*self.border_thickness)
        #
        #         args = (x, y, h, w, *_)
        #
        #         result = attr(*args, **kwargs)
        #         return result
        #     return new_setGeometry
        # return attr


    # def __getattribute__(self, name):
    #     attr = super().__getattribute__(name)
    #
    #     if name == "setGeometry" and callable(attr):
    #         def new_setGeometry(*args, **kwargs):
    #             x, y, h, w, *_ = args
    #
    #             print(x, y, h, w, *_)
    #             x += int(self.border_thickness)
    #             y += int(self.border_thickness)
    #             h -= int(2*self.border_thickness)
    #             w -= int(2*self.border_thickness)
    #
    #             args = (x, y, h, w, *_)
    #
    #             result = attr(*args, **kwargs)
    #             return result
    #         return new_setGeometry
    #     return attr


class JpWidget(QWidget, Frame):
    def __init__(self, parent=None):
        QWidget.__init__(self,  parent=parent)
        Frame.__init__(self, border_thickness=5)

    def paintEvent(self, event):

        painter = QPainter(self)

        brush = QBrush(QColor(255, 0, 255), Qt.SolidPattern)
        painter.setBrush(brush)

        # pen = QPen(QColor("black"), 5, Qt.SolidLine)
        painter.setPen(Qt.NoPen)

        W = self.width()
        H = self.height()

        painter.drawRect(0,0, W, H)

        self.draw_frame( )

# class JpPushButton(QPushButton, Frame):
#     def __init__(self, parent=None):
#         QPushButton.__init__(self, parent=parent, text="Jump Machine")
#         Frame.__init__(self, parent=parent)

class JpPushButton(QPushButton, Frame):
    def __init__(self, text = "None", parent=None ):
        QPushButton.__init__(self, text=text, parent=parent)
        Frame.__init__(self, border_thickness=5)

        self.clicked.connect( self.pushWork )

    def pushWork(self):
        print("push work")

    def paintEvent(self, event):
        painter = QPainter(self)

        if self.isDown():
            color = QColor(255, 0, 0)
        elif self.underMouse():
            color = QColor(255, 127, 0)
        else:
            color = QColor(0, 255, 0)

        painter.setBrush(color)
        painter.setPen(QPen(Qt.black, 2))
        painter.drawRect(self.rect().adjusted(0, 0, 0, 0))

        painter.drawText(self.rect(), Qt.AlignCenter, self.text())

        self.draw_frame()

    def enterEvent(self, event):
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.update()
        super().leaveEvent(event)



from PyQt5.QtWidgets import QApplication, QMainWindow
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.setWindowTitle("Jumping Machine")
        self.setGeometry(50, 50, 600, 600)
        self.setFixedSize(600, 600)

        win = QWidget(self)
        win.setStyleSheet(f"""background-color: yellow;""")
        self.setCentralWidget( win )

        # self.f1 = Frame( win , 100, 100)
        self.JpWidget = JpWidget( win )
        self.JpWidget.setGeometry(100, 100, 100, 100)
        self.JpWidget.setStyleSheet(f"""background-color: blue;""")


        self.w1 = QWidget( win)
        self.w2 = QWidget( win)
        self.w3 = QWidget(win)
        self.w4 = QWidget(win)

        self.w1.setGeometry(0, 0, 100, 100)
        self.w2.setGeometry(200, 200, 100, 100)
        self.w3.setGeometry(100, 100, 10, 10)
        self.w4.setGeometry(200-10, 200-10, 10, 10)

        self.w1.setStyleSheet(f"""background-color: pink;""")
        self.w2.setStyleSheet(f"""background-color: pink;""")
        self.w3.setStyleSheet(f"""background-color: orange;""")
        self.w4.setStyleSheet(f"""background-color: orange;""")


        self.button = JpPushButton("Jump Machine", self)
        self.button.setGeometry(300, 0, 100, 100)


app = QApplication(sys.argv)

win = MainWindow()
win.show()

sys.exit(app.exec_())