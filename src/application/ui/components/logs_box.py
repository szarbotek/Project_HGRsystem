from PyQt5.QtWidgets import QPlainTextEdit


class LogsBox(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setReadOnly(True)
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: white;
                color: black;
                font-family: Consolas;
                font-size: 10pt;
            }
        """)

    def refresh(self, new_text:str ):

        # pozycja suwaka (scrollbara) i kursora
        cursor = self.textCursor()
        old_position = cursor.position()
        scrollbar_pos = self.verticalScrollBar().value()

        # teks update
        self.setPlainText(new_text)

        # renew pozycji kursora o suwaka
        new_cursor = self.textCursor()
        new_cursor.setPosition(min(old_position, len(new_text)))
        self.setTextCursor(new_cursor)

        self.verticalScrollBar().setValue(scrollbar_pos)