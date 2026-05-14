from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtCore import Qt


class StaticIconImage(QWidget):
    def __init__(self, parent=None, path="", size=100):
        super().__init__(parent)

        self._pixmap = QPixmap(path)
        self._size = size

        self.setFixedSize(size, size)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

    def paintEvent(self, event):
        if self._pixmap.isNull():
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        pixmap = self._pixmap.scaled(
            self.width(),
            self.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        x = (self.width() - pixmap.width()) // 2
        y = (self.height() - pixmap.height()) // 2

        painter.drawPixmap(x, y, pixmap)

class DoubleIconImage(QWidget):
    """
        Icona dwustanow. Pozwala na wyśiwetlanie dwóch stanów ikony ON/OFF zależnie od wewnętrznej fagi

    """
    def __init__(self, parent=None, pathAcc:str="", pathDis:str="", base_state:bool = False,  size=100):
        super().__init__(parent)

        self._pixmapAcc = QPixmap(pathAcc)
        self._pixmapDis = QPixmap(pathDis)
        self.FALG_state = base_state

        if not self._pixmapAcc.isNull():
            ratio = self._pixmapAcc.width() / self._pixmapAcc.height()
            # Jeśli szerokość > wysokość, size to szerokość. Jeśli nie, size to wysokość.
            if ratio > 1:
                self.setFixedSize(size, int(size / ratio))
            else:
                self.setFixedSize(int(size * ratio), size)
        else:
            self.setFixedSize(size, size)

        self.setAttribute(Qt.WA_TransparentForMouseEvents)

    def set_state(self, flag_of_state:bool):
        self.FALG_state = flag_of_state

    def paintEvent(self, event):

        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        ico = self._pixmapAcc if self.FALG_state else self._pixmapDis

        pixmap = ico.scaled(
            self.width(),
            self.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        x = (self.width() - pixmap.width()) // 2
        y = (self.height() - pixmap.height()) // 2

        painter.drawPixmap(x, y, pixmap)

class MultiIconImage(QWidget):
    """
        Icona dwustanow. Pozwala na wyśiwetlanie dwóch stanów ikony ON/OFF zależnie od wewnętrznej fagi

    """
    def __init__(self, parent=None, paths:list[str]=["None"], index:int = 0,  size=100):
        super().__init__(parent)

        self.index = index
        self.ico_paths = paths
        self._pixmapAcctive = QPixmap(paths[index])

        if not self._pixmapAcctive.isNull():
            ratio = self._pixmapAcctive.width() / self._pixmapAcctive.height()
            # Jeśli szerokość > wysokość, size to szerokość. Jeśli nie, size to wysokość.
            if ratio > 1:
                self.setFixedSize(size, int(size / ratio))
            else:
                self.setFixedSize(int(size * ratio), size)
        else:
            self.setFixedSize(size, size)

        self.setAttribute(Qt.WA_TransparentForMouseEvents)

    def next(self):
        self.index += 1
        if self.index >= len(self.paths):
            self.index = 0

    def prev(self):
        self.index -= 1
        if self.index < 0:
            self.index = len(self.paths) - 1

    def paintEvent(self, event):
        try:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

            self._pixmapAcctive =  QPixmap(self.ico_paths[self.index])

            ico = self._pixmapAcctive

            pixmap = ico.scaled(
                self.width(),
                self.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

            x = (self.width() - pixmap.width()) // 2
            y = (self.height() - pixmap.height()) // 2

            painter.drawPixmap(x, y, pixmap)
        except Exception as e:
            print(e)