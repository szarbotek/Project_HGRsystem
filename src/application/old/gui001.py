import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QGridLayout, QLabel, QFrame, QPushButton)
from PyQt5.QtCore import Qt


class ModernDataPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Robot Status")
        self.setFixedWidth(250)  # Mniejsze, kompaktowe pole
        self.setStyleSheet("background-color: #121212;")

        # Główny układ pionowy
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)

        # 1. PRZYCISK
        self.toggle_btn = QPushButton("Pokaż szczegóły")
        self.toggle_btn.setCheckable(True)  # Przycisk działa jak przełącznik
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
                font-family: 'Segoe UI';
            }
            QPushButton:hover { background-color: #2980b9; }
            QPushButton:checked { background-color: #2c3e50; text: "Ukryj dane"; }
        """)
        self.toggle_btn.clicked.connect(self.setup_data)
        self.main_layout.addWidget(self.toggle_btn)

        # 2. RAMKA Z DANYMI (Kontener)
        self.info_frame = QFrame()
        self.info_frame.setVisible(True)  # Domyślnie ukryte
        self.info_frame.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border: 1px solid #333;
                border-radius: 8px;
            }
            QLabel { color: #bbb; font-size: 11px; }
            .Value { 
                color: #00ffaa; 
                background: #252525; 
                padding: 2px 6px; 
                border-radius: 4px;
                font-family: 'Consolas';
            }
        """)

        # Układ wewnątrz ramki
        self.info_layout = QGridLayout(self.info_frame)
        # self.setup_data()

        self.main_layout.addWidget(self.info_frame)
        self.main_layout.addStretch()

    def setup_data(self):
        # Mniejsza czcionka i bardziej kompaktowy układ
        data = [
            ("Tool", "tool0"),
            ("WorkObj", "wobj0"),
            ("Payload", "load0"),
            ("Status", "Stopped"),
            ("Status", "Stopped"),
        ]

        for row, (k, v) in enumerate(data):
            key_lbl = QLabel(k)
            val_lbl = QLabel(v)
            val_lbl.setProperty("class", "Value")
            val_lbl.setAlignment(Qt.AlignCenter)

            self.info_layout.addWidget(key_lbl, row, 0)
            self.info_layout.addWidget(val_lbl, row, 1)

    def toggle_details(self):
        # Przełączanie widoczności
        is_visible = self.info_frame.isVisible()
        self.info_frame.setVisible(not is_visible)

        # Zmiana tekstu na przycisku
        self.toggle_btn.setText("Ukryj dane" if not is_visible else "Pokaż szczegóły")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = ModernDataPanel()
    demo.show()
    sys.exit(app.exec_())