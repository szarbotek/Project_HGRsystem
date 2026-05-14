from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush
from PyQt5.QtCore import Qt, QRectF

from application.ui.components.jumping_machine import JumpingMachine

from typing import Dict

class JpWidget(QWidget, JumpingMachine):
    thickness: int = 5

    color_mode: Dict[bool, QColor] = {
        False: QColor(0, 0, 0),
        True: QColor(255, 0, 0),
    }

    def __init__(self, parent=None ):
        super().__init__( parent=parent, parentJP=parent, instanceJP=self)
        self.color_background = QColor(255,255,255)

        self.FLAG_is_object_selected = False

    def paintEvent(self, event):
        painter = QPainter(self)

        ## Włączenie antyaliasingu
        painter.setRenderHint(QPainter.Antialiasing)

        color_border = self.color_mode[self.FLAG_is_object_selected]

        half = self.thickness / 2

        ## Definicja obszaru rysowania
        rect = QRectF(self.rect()).adjusted( half, half, -half, -half )

        ## Ustawienie tła
        painter.setBrush(QBrush(self.color_background))

        ## Ustawienie ramki (1px, ciemnoszary)
        pen = QPen( color_border )
        pen.setWidth(self.thickness)
        painter.setPen(pen)

        ## Rysowanie prostokąta z zaokrągleniem 10px
        painter.drawRoundedRect(rect, 10.0, 10.0)


if __name__ == '__main__':

    from PyQt5.QtWidgets import QApplication, QMainWindow
    import sys

    class MainWindow(QMainWindow):
        def __init__(self):
            QMainWindow.__init__(self)

            self.setWindowTitle("Jumping Machine")
            self.setGeometry(50, 50, 600, 600)
            self.setFixedSize(600, 600)


            win = JpWidget( self )
            win.setGeometry(50,50,50,50)


    app = QApplication(sys.argv)

    win = MainWindow()
    win.show()

    sys.exit(app.exec_())