from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QBrush
from PyQt5.QtCore import Qt


from application.ui.components.jumping_machine import JumpingMachine


class JpWidget(QWidget, JumpingMachine):
    def __init__(self, parent=None):
        super().__init__( parent=parent, parentJP=parent, instanceJP=self)

    def paintEvent(self, event):

        painter = QPainter(self)

        brush = QBrush(QColor(255, 0, 255), Qt.SolidPattern)
        painter.setBrush(brush)

        # pen = QPen(QColor("black"), 5, Qt.SolidLine)
        painter.setPen(Qt.NoPen)

        W = self.width()
        H = self.height()

        painter.drawRect(0,0, W, H)


from PyQt5.QtWidgets import QApplication, QMainWindow
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.setWindowTitle("Jumping Machine")
        self.setGeometry(0, 50, 600, 600)
        self.setFixedSize(600, 600)

        w1 = JpWidget(self)
        w1.setGeometry(0, 50,100,100)

        w2 = JpWidget(self)
        w2.setGeometry(150, 50, 100, 100)

        JumpingMachine.set_cursor( w1 )
        JumpingMachine.generate_connetion()

    def keyPressEvent(self, event):
        try:
            # wysyłanie sygnałów ruchu do kursora
            if JumpingMachine.FLAG_is_connection_generate:
                if event.key() == Qt.Key_W:
                    JumpingMachine.movement_courser.jump('W')
                elif event.key() == Qt.Key_S:
                    JumpingMachine.movement_courser.jump('S')
                elif event.key() == Qt.Key_A:
                    JumpingMachine.movement_courser.jump('A')
                elif event.key() == Qt.Key_D:
                    JumpingMachine.movement_courser.jump('D')
                elif event.key() == Qt.Key_Q:
                    JumpingMachine.movement_courser.jump('OUT')
                elif event.key() == Qt.Key_E:
                    JumpingMachine.movement_courser.jump('IN')
            else:
                print("Not generate connections")
        except Exception as e:
            print(e)




app = QApplication(sys.argv)

win = MainWindow()
win.show()

sys.exit(app.exec_())