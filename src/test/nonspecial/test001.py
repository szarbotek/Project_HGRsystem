import shutil
import os
import random

"""
    kopiowanie plików

"""
pathA = "image//valid"
pathB = "image//test"
nazwa_pliku = "jojo.png"
cel_pliku = "jojo2.png"

# Tworzymy pełne ścieżki
zrodlo = os.path.join(pathA, nazwa_pliku)
cel = os.path.join(pathB, cel_pliku)

# Kopiowanie
try:
    shutil.copy2(zrodlo, cel)
    print(f"Plik {nazwa_pliku} został pomyślnie skopiowany do {pathB}")
except FileNotFoundError:
    print("Błąd: Nie znaleziono pliku źródłowego.")
except PermissionError:
    print("Błąd: Brak uprawnień do zapisu w folderze docelowym.")
