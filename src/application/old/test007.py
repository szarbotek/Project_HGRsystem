from typing import Sequence, List
import numpy as np

class CellularAutomaton:
    """
        Automat posiada wektor wejściowy 9 próbek, na ich podstawie zwraca wekro adekwatnej długości zapewniajacy na
        okreslenie przejścia między grupami. Automat może zwrócić wektor reprezentujący do 3 grup.

        Podczas pracy wykonywane są następujące kryteria:
            1. "Dominacją strony" Na każde z 9 próbek przypada 1 wektor analizy, który sprawdza sąsiedztwo do 2 próbek.
            Jeśli któraś ze stron posiada wartość dominującą to nadpisuje ona wartośc próbki.

            2. "Dominacja względem próbki" Jeśli 2 strony posiadają wartość dominująca,
            następuje nadpisanie zgodnie z wartościa próbki (zgodna wartość próbki powoduje pozostawienie wartości próbki).

            3. "Dominacja względem środka" Jeśli natomiast próbka nie decydyje o wyniku sprawdzana jest pozycja próbki
            względem środka wektora. Wybrana zostaje strona bliższa środkowi

            4. "Trwałość dziur granicznych" Jeśli na 5 granicznych próbkach zwyłaczeniem skrajnej próbki powstała dziura
            na 4 próbki (wartości 0) to wartości tych próbek nie mogą zostać nadpisane.
    """
    def __init__(self, Q: Sequence[int]):
        """
            Inicjacja warunków poczatkowych automatu.
        """
        self.Q_0 =  np.array(Q)
        self.Q_state: List[Sequence] = [self.Q_0]

    def run(self):
        """
            Uruchomienie automatu do czasu osiągnięcia stabilności układu.
        """
        Q_last = self.Q_0
        Q = self.Q_0

        while True:
            Q = self.next_state( Q )
            if np.array_equal(Q, Q_last) :
                break
            else:
                Q_last = Q

        return Q_last

    def next_state(self, Q_t: Sequence[int])->Sequence[int]:
        """
            Iteracja jednego przejścia automatu komórkowego
        """

        Q_t = np.array(Q_t)

        V = np.concatenate([[-1, -1], Q_t, [-1, -1]])

        T = np.row_stack([V[n:n + 5] for n in range(0, 9)])

        U = []
        for trr in T:
            urr = []
            for t in trr:
                if t == -1:
                    urr.append(trr[2])
                else:
                    urr.append(t)
            U.append(np.array(urr))
        U = np.array(U)

        E = lambda X, Y: (X if X == Y else 0)
        D = lambda X, Y: (0 if X + Y == 0 else (X or Y))
        C = lambda X, Y: (X or Y)

        W = []
        X = []
        Z = []
        Y = []
        for urr in U:
            wrr = []
            xrr = []
            zrr = []
            yrr = []

            wrr.append(E(urr[0], urr[1]))
            wrr.append(urr[2])
            wrr.append(E(urr[3], urr[4]))

            xrr.append(E(wrr[0], wrr[1]))
            xrr.append(E(wrr[1], wrr[2]))

            zrr.append(C(xrr[0], xrr[1]))

            yrr.append(D(wrr[0], wrr[2]))
            yrr.append(D(wrr[2], wrr[0]))

            W.append(wrr)
            X.append(xrr)
            Z.append(zrr)
            Y.append(yrr)

        W = np.array(W)
        X = np.array(X)
        Z = np.array(Z)
        Y = np.array(Y)

        Q_tp1 = []
        for i, (zrr, yrr) in enumerate(zip(Z, Y)):
            if zrr[0] != 0:
                Q_tp1.append(zrr[0])
            else:
                s = 1 if i < len(Q_t) / 2 else 0
                Q_tp1.append(yrr[s])

        Q_tp1 = np.array(Q_tp1)
        if np.all(Q_t[1:5] == 0):
            Q_tp1[1:5] = 0
        if np.all(Q_t[4:8] == 0):
            Q_tp1[4:8] = 0

        return Q_tp1



def jump_condtion(tab: List[str], active_lb) -> (bool, str | None):
    """
        Funkcja okresla werunek przeskaku poprzez analize pierwszych 9 próbek co przekłada się na 900ms analizy czasowej
        przy czym analiza odbywa sie od 5 próbki wobec czego opóźnienie przeskoku wynosi 500ms analizy czasowej.

        Przeprocesowana tablica przez automat pozwala na uzyskania stanu:

        1. Płynne przejście
        2. Stała wartość
        3. Impuls
        4. Dziura przerwania

        Przeskok jest uwarunkowany zmianą etykiety klasy w punkcie środkowym tablicy

    """
    ## budowa enkodera i dekodera etykiet klas dla wektora, uwzględnia on przypadek "None", i nie zaczyna
    ## numeracji od 0 co jest kluczowe dla działania dziur automatu
    lb_encoder = {ut: i + 1 for i, ut in enumerate(set(tab))}
    lb_encoder.update({"None": 0})

    lb_decoder = {v: k for k, v in lb_encoder.items()}

    ## utworzenie wektora wejściowego
    Q_0 = [lb_encoder[t] for t in tab]

    ## inicjacja modelu
    CA = CellularAutomaton(Q_0)

    ## uruchomienie modelu
    Q_stable = CA.run()

    ## odczytwanie wartości wektora wyjsciowego
    tab_process = [lb_decoder[q] for q in Q_stable]

    print(tab_process)

    ## porównanie etykiety środkowej, wywołanie przeskoku
    if tab_process[4] != active_lb:
        return True, tab_process[4]
    else:
        return False, None


print( jump_condtion(  ["fist","fist","call","stop", "call","stop", "fist","stop","stop",], "fist" ) )