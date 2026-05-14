import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter, QColor, QFont, QPen
from PyQt5.QtCore import Qt, QRectF


class DisplayData(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        # Inicjalizacja zmiennych wyglądu
        self.bg_color = QColor(45, 157, 245)  # Kolor tła (niebieski)
        self.box_color = QColor(255, 255, 255)  # Kolor pól (biały)
        self.padding = 10  # Margines od krawędzi
        self.spacing = 10  # Odstęp między polami

        self.data = {}

    def set_data(self, data_dict):
        """Ustawia nowy słownik i odświeża widok."""
        self.data = data_dict
        self.update()

    def update_data(self, data_dict):
        """Aktualizuje wartości dla istniejących kluczy."""
        for key, value in data_dict.items():
            if key in self.data:
                self.data[key] = str(value)
        self.update()

    def paintEvent(self, event):
        if not self.data:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 1. Rysowanie tła panelu
        painter.setBrush(self.bg_color)
        painter.setPen(QPen(Qt.black, 2))
        painter.drawRect(self.rect().adjusted(1, 1, -1, -1))

        # 2. Obliczanie wymiarów
        rows = len(self.data)
        # Szerokość: (Całość - marginesy boczne - odstęp środkowy) / 2
        cell_width = (self.width() - (2 * self.padding) - self.spacing) / 2
        # Wysokość: (Całość - marginesy góra/dół - sumaryczne odstępy między wierszami) / liczba wierszy
        cell_height = (self.height() - (2 * self.padding) - ((rows - 1) * self.spacing)) / rows

        painter.setFont(QFont("Segoe UI", 12, QFont.Bold))

        # 3. Rysowanie wierszy
        for i, (key, value) in enumerate(self.data.items()):
            y_offset = self.padding + i * (cell_height + self.spacing)

            # Definicja obszarów dla lewego (klucz) i prawego (wartość) pola
            left_rect = QRectF(self.padding, y_offset, cell_width, cell_height)
            right_rect = QRectF(self.padding + cell_width + self.spacing, y_offset, cell_width, cell_height)

            # Rysowanie białych pudełek
            painter.setBrush(self.box_color)
            painter.setPen(QPen(Qt.black, 2))
            painter.drawRoundedRect(left_rect, 10, 10)
            painter.drawRoundedRect(right_rect, 10, 10)

            # Rysowanie tekstu
            painter.setPen(Qt.black)
            painter.drawText(left_rect, Qt.AlignCenter, str(key))
            painter.drawText(right_rect, Qt.AlignCenter, str(value))


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Przykładowe dane
    my_data = {"X": "Ø", "Y": "1", "D": "5"}

    window = DisplayData()
    window.set_data(my_data)
    window.setWindowTitle("Widżet Danych")
    window.resize(350, 250)
    window.show()

    sys.exit(app.exec_())