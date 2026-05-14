
class MetaMOV(type):
    # Ta metoda odpowiada za to, co wyświetla print(NazwaKlasy)
    def __str__(cls):
        return "Hello dot"

    # Repr jest przydatne, gdy klasa jest np. w liście
    def __repr__(cls):
        return "Hello dot"

class MOV(metaclass=MetaMOV):
    pass

# Teraz możesz to wywołać tak, jak chciałeś:
print(MOV)  # Wynik: Hello
x = MOV

"pinky " + MOV