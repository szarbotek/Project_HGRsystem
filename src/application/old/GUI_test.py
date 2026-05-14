import sys

import mediapipe as mp
from mediapipe.tasks import python as mp_python

from PyQt5.QtWidgets import QApplication, QWidget



# Utworzenie aplikacji
app = QApplication(sys.argv)

# Utworzenie głównego okna
window = QWidget()
window.setWindowTitle("Moja pierwsza aplikacja PyQt5")
window.resize(400, 300)

# Wyświetlenie okna
window.show()

# Uruchomienie pętli aplikacji
sys.exit(app.exec_())