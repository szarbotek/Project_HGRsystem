"""
    Obiekt generuje QWiget wyświetlający status kolejki typu: Circular Buffer
"""

from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import  QFont, QPainter, QPen, QColor, QBrush
from PyQt5.QtCore import Qt, QRect, QRectF


from typing import List, Literal, Sequence


class WordQueue(QWidget):
    """
        Obiekt pozwala na wyświetlanie kolejki typu: Circular Buffer

    """

    def __init__(self, parent=None, max_place_box:int=5, stick_to_side: Literal["Right", "Left", "", "Up", "Down"] = "Left"):
        super().__init__(parent=parent)

        ## dane kolejki
        self.data: List[str] = []
        ## liczba pól do wyświetlania
        self.max_place_box = max_place_box

        ## parametry
        self.stick_to_side = stick_to_side
        self.color_background = QColor("#ff0000")

        self.font_size = 8

    def new_data(self, dataset: Sequence[str], text_f:str=r"{}"):
        try:
            assert isinstance(dataset, Sequence), TypeError( f"<ERR:{self.__class__}> Probelem {self.__class__.__name__}" )

            self.data = [ text_f.format(d) for d in dataset]
        except Exception as e:
            print(f"\n<ERR:{self.__class__}>" ,e, dataset, text_f)

    def paintEvent(self, event):
        painter = QPainter(self)

        ## wygładzanie
        painter.setRenderHint(QPainter.Antialiasing)

        width = self.width()
        height = self.height()

        ## Rysowanie pola tła
        rect  = QRectF(self.rect())
        painter.setBrush( QBrush(self.color_background) )

        pen = QPen( QColor(255, 255, 255) )
        pen.setWidth(2)
        painter.setPen(pen)

        ## pole kolejki
        painter.drawRoundedRect( rect, 15, 15)

        if self.stick_to_side in ["Right", "Left"]:
            box_width = int(width/self.max_place_box)
            box_height = height
        else:
            box_width = width
            box_height = int(height/ self.max_place_box)

        padd = 5
        padd2 = padd + padd

        for i, word in enumerate(self.data):
            x = 0
            y = 0
            if self.stick_to_side == "Left":
                x = box_width * i
                y = 0
            if self.stick_to_side == "Right":
                x = width - (box_width * (i+1))
                y = 0
            if self.stick_to_side == "Up":
                x = 0
                y = (box_height) * (i)
            if self.stick_to_side == "Down":
                x = 0
                y = height - (box_height * (i+1) )

            rect =  QRect( x+padd, y+padd, box_width-padd2, box_height-padd2)

            ## pole na tekst
            painter.setPen( QPen( QColor(0, 0, 0) , 2))
            painter.setBrush(  QColor(255, 255, 255) )
            painter.drawRoundedRect( rect, 10, 10)

            ## tekst
            painter.setPen( QColor(0, 0, 0) )
            painter.setFont(QFont("Segoe UI", self.font_size, QFont.Bold))
            painter.drawText(rect, Qt.AlignCenter, word )

