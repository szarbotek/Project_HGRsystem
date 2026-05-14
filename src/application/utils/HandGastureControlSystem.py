"""

"""
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from pip._internal import commands

from sklearn.preprocessing import LabelEncoder

from data.project_values import LOG, FALG_NORMALIZATION
from src.func.special import MODEL_H5, NPY
from src.func.analyzing_tool import normalization, landmark2array
from src.application.utils.structure import T_LeftRight, CircularBuffer
from src.application.core.CMT import T_TagCommand, CommunicationTags

from enum import Enum
from typing import List, Dict, Tuple, Sequence, Any

import numpy as np

import traceback

import time

class Task:
    """
        Task jest strukturą danych posiadającą kolejkie N elementową jako kontener na słowa.

        Dane są przechowwyane w postaci pakietów zawierających nazwę etykiet sprzężoną z czasem trwania wywyołania etykiety.
    """

    max_data_gesture: int = 5

    def __init__(self, max_word: int = 3, time_limit_ms: int = 8000):

        ## ilosć gestów w kolejce
        self.max_word = max_word
        ## kolejka dancyh
        self.data: CircularBuffer = CircularBuffer(max_word)

        ## maksumalny zakres przetwarzania gestów
        self.time_limit_ms = time_limit_ms#ms

        # for _ in range(0, max_word+1):
        ## ustawienie domyślenj 1 wartości kolejki
        self.data.put({"None": 0})

        ## Flaga określa czy w danej próbce nastąpił przeskok, jest on aktywny do chwili kolejnego sprawdzenia przezskoku
        self.FLAG_jump_active:bool = False

        ## aktywacja ostaniego słowa
        self.active_word: str = "None"

    ## ustawienie aktywnego słowa
    def set_active_word(self, last_word: str):
        self.active_word: str = last_word

    ## przedluzenie aktywnego gestu
    def update(self, time_interval_ms: int):

        ## zwiększenie interwału czasowego gestu
        self.data.first[self.active_word] += time_interval_ms

        ## korekcja kolejki wzlgędem limitu czasu
        self.fit_to_time_limit(time_interval_ms)

    ## dodanie nowego gestu
    def new(self, lb: str, time_interval_ms: int):
        ## wstawienie gestu do kolejki
        self.data.put( {lb: time_interval_ms} )
        ## przypisanie ostatniego wstawionego gestu
        self.set_active_word( lb )

        ## korekcja kolejki wzlgędem limitu czasu
        self.fit_to_time_limit( time_interval_ms )

    def fit_to_time_limit(self, time_interval_ms:int):
        """
            Metoda ma nakładać limit na słowa. Jeśli suma czasów poszczególnych słów jest większa niż zaznaczony limit
            następuje zminiejszenie wartości ostatniego gesto. Jesli jego wartośc spadnie do minimum zostaje on
            wyżucony z kolejki.
        """

        buff: List[Dict[str, int]] = self.data.buffer.copy()

        if len(buff) >= 2:
            ## Dwa lub więcej gestów w kolejce

            ## zsumowanie czasów poszcególnych gestów
            complete_time_ms = sum( sum( word.values() ) for word in buff )

            ## analiza przekorzecznia limitu czasowego
            if complete_time_ms > self.time_limit_ms:
                ## pobranie pierwszej i jedynej pary etykieta, czas
                lb, time_ms = next(iter(self.data.last.items()))

                ## zmniejszenie interwału czasowego ostatniego gestu
                self.data.last[lb] -= time_interval_ms
                ## decycja o usunięciu gestu z kolejki
                if time_ms-time_interval_ms <= 0:
                    self.data.throw()
        else:
            ## W kolejce znajduje się tylko jeden gest

            ## pobranie pierwszej i jedynej pary etykieta, czas
            lb, time_ms = next(iter(self.data.first.items()))
            ## zablokowanie inkrementu czasowego
            if time_ms >= self.time_limit_ms:
                self.data.first[lb] = self.time_limit_ms

    def get_label(self):
        return [ next(
                    iter(d.keys())
                )
                for d in self.data.get_buffer()
        ]

    def get_value(self):
        return [ next(
                    iter(d.values())
                )
                for d in self.data.get_buffer()
        ]

    def get_data(self):
        return self.data.get_buffer()

    ## zwraca i-ty element Circle Buffer
    def get_data_index(self, index: int):
        return self.data.get_buffer_index(index)

    def find_label_contain_time_range(self, t_s:int, t_f:int)-> str:
        """
            Fukcja sprawdza czy podany zakres czasowy jest przypisany do pojedyńczej etykiety czasowej
        """
        t_c:int = 0 ## poczatek etykiety czasowej
        t_m:int = -1 ## koniec etykiety czasowej
        ## ograniczenie do zekresu czasowego
        if t_f > self.time_limit_ms: t_f = self.time_limit_ms

        ## iteracja po kolejnych etykietach
        for d in self.data.get_buffer():
            lb, time = next(iter(d.items()))
            t_m = time
            ## sprawdzenie czy szukany zakres znajduje się w jednej etykiecie
            chk1:bool = t_c <= t_s <= t_m
            chk2:bool = t_c <= t_f <= t_m
            ## jesłi jeden znajduje się w zakresie
            if chk1 or chk2:
                ## jeśli dwa znajdują się w zakresise
                if chk1 and chk2:
                    return lb
                ## jeśli tylko jeden faktycznie znajduje się w zakresie, przerywane zostaje poszuiwanie
                else:
                    break
            else:
                ## zwiekszenie dolnego zakresu o rozmiar obecnej etykiety
                t_c += t_m
                continue
        ## zwrot ogólnej etykiety
        return "None"

    def __str__(self):
        return "<task>: " + str(self.data)


# noinspection PyTypeChecker
class WordCoder:

    class HOTKEY_PROGRAM(str, Enum):
        HOTKEY_RUN_1 = "HGR_1"
        HOTKEY_RUN_2 = "HGR_2"
        HOTKEY_RUN_3 = "HGR_3"

    class LABEL(str, Enum):
        """
            KLasa reprezentuje etykiery kodowania, zgodne z etykietami gestów. Klasa ma również 2 dodatkowe elementy
            star reprezentująca dowolny gest,oraz non reprezentująca brak gestu.
        """
        call = "call"
        dislike = "dislike"
        fist = "fist"
        grip = "grip"
        like = "like"
        little_finger = "little_finger"
        one = "one"
        peace = "peace"
        rock = "rock"
        stop = "stop"
        three = "three"
        three3 = "three3"
        thumb_index = "thumb_index"
        non = "None"
        star = "*"

    class INFO(str, Enum):
        GUI = "GUI"
        ROBOT_SERVER = "ROBOT-SERVER"

    class QUESTION(str, Enum):
        NEW = "NEW"
        ##
        MOV = "MOV"
        INTERACT = "INTERACT"
        ##
        CONNECT = "CONNECT"
        ##
        RUNSYS = "RUNSYS"
        ##
        MOVSYS = "MOVSYS"

        CONTROL_PROMPT = ">>"

    class COMMAND(str, Enum):
        DO = "DO"
        CLC = "CLC"
        END = "END" ## ma za zadanie zakończyć prace obecnego odpytania i wyczyści kolejkę
        BREAK = "BREAK" ## przerywa obecne odpytanie, ale pozostawia nowy stan odpytania
        FINISH = "FINISH" ## dodany do kolejki odpowiada za przerwanie w zapytania

    class OPTION(str, Enum):
        ## opcje MOV
        SITE_RL = "SITE_RL"
        SITE_UD = "SITE_UD"
        SITE_IO = "SITE_IO"
        LEFT = "LEFT"
        RIGHT = "RIGHT"
        UP = "UP"
        DOWN = "DOWN"
        IN = "IN"
        OUT = "OUT"
        ## ITERACT
        SELECT = "SELECT"
        PUSH_BUTTON = "PUSH_BUTTON"
        SLIDER = "PUSH_BUTTON"
        ACTIVATE_OBJECT = "ACTIVATE_OBJECT"
        DEACTIVATE_OBJECT = "DEACTIVATE_OBJECT"
        END_INTERACT = "END_INTERACT"
        ## CONNECT
        ENABLE = "ENABLE"
        DISABLE = "DISABLE"
        # SELECT = ...
        INCREMENT = "INCREMENT"
        DECREMENT = "DECREMENT"
        PICK = "PICK"
        NEXT = "NEXT"
        PREV = "PREV"
        RUN = "RUN"
        STOP = "STOP"
        RESUME = "RESUME"
        ## MOVSYS
        X_PLUS = "X_PLUS"
        X_MINUS = "X_MINUS"
        Y_PLUS = "Y_PLUS"
        Y_MINUS = "Y_MINUS"
        Z_PLUS = "Z_PLUS"
        Z_MINUS = "Z_MINUS"

    class DYNAMIC:
        class SelfStr_NUMERATOR(type):
            def __str__(cls) -> str: return str(cls.value)

        class NUMERATOR(metaclass=SelfStr_NUMERATOR):
            def __init__(self, value:int=0, range_:int=5):
                self.value = value
                self.range = range_

            def setup(self, value:int, range_:int):
                self.value = value
                self.range = range_

            def increment(self):
                self.value += 1
                if self.value >= self.range:
                    self.value = 0

            def decrement(self):
                self.value -= 1
                if self.value < 0:
                    self.value = self.range

            def __str__(self):
                return str(self.value)

        class SelfStr_LITERAL_LIST(type):
            def __str__(cls) -> str: return str(cls.objects_list[cls.index])

        class LITERAL_LIST(metaclass=SelfStr_LITERAL_LIST):
            def __init__(self, index=0, object_list = None):
                self.objects_list: Sequence[Any] = object_list
                self.index = index
                self.range = len(self.objects_list)

            def setup(self, index:int, object_list:Sequence[Any] ):
                self.objects_list = object_list
                self.index = index
                self.range = len(self.objects_list)

            def next(self):
                self.index += 1
                if self.index >= self.range:
                    self.index = 0

            def prev(self):
                self.index -= 1
                if self.index < 0:
                    self.index = self.range - 1

            def __str__(self):
                return str(self.objects_list[self.index])


    numerator_connect: DYNAMIC.NUMERATOR =  DYNAMIC.NUMERATOR(0, 3)
    literal_programs: DYNAMIC.LITERAL_LIST = DYNAMIC.LITERAL_LIST(0, ["None1", "None2", "None3"])

    main_hand = { ## Aby aktywować zasobnik command_hand na końcu powinno być przypisane odpowiednie przekierowanie
        LABEL.stop + LABEL.rock: [ QUESTION.NEW, INFO.GUI, QUESTION.MOV ],
        LABEL.rock + LABEL.star: [ COMMAND.END ],
        LABEL.stop + LABEL.one:  [ QUESTION.NEW, INFO.GUI, QUESTION.INTERACT ],
        LABEL.one  + LABEL.star: [ COMMAND.BREAK ],
        LABEL.stop + LABEL.call: [ QUESTION.NEW, INFO.ROBOT_SERVER, QUESTION.CONNECT ],
        LABEL.call + LABEL.star: [ COMMAND.END ],
        LABEL.stop + LABEL.grip: [ QUESTION.NEW, INFO.ROBOT_SERVER, QUESTION.RUNSYS ],
        LABEL.grip + LABEL.star: [ COMMAND.END],
        LABEL.stop + LABEL.thumb_index: [QUESTION.NEW, INFO.ROBOT_SERVER, QUESTION.MOVSYS],
        LABEL.thumb_index + LABEL.star: [COMMAND.END],

        # LABEL.star + LABEL.call: QUESTION.CONTROL_PROMPT,
    }
    command_hand = {
        QUESTION.MOV: {
            LABEL.star + LABEL.like:          [OPTION.SITE_RL, OPTION.RIGHT, COMMAND.DO],
            LABEL.star + LABEL.thumb_index:   [OPTION.SITE_RL, OPTION.LEFT, COMMAND.DO],
            LABEL.star + LABEL.rock:          OPTION.SITE_UD,
            LABEL.rock + LABEL.three3:        [OPTION.UP, COMMAND.DO],
            LABEL.rock + LABEL.little_finger: [OPTION.DOWN, COMMAND.DO],
            LABEL.fist + LABEL.stop:           OPTION.SITE_IO,
            LABEL.stop + LABEL.one:           [OPTION.IN, COMMAND.DO],
            LABEL.stop + LABEL.peace:         [OPTION.OUT, COMMAND.DO],
            LABEL.call + LABEL.like:          [COMMAND.DO],
            LABEL.call + LABEL.dislike:       [COMMAND.CLC],
        },
        QUESTION.INTERACT: {
            LABEL.star + LABEL.thumb_index:   [COMMAND.BREAK,  QUESTION.NEW, INFO.GUI, QUESTION.INTERACT, OPTION.SELECT],
            LABEL.thumb_index + LABEL.one:    OPTION.PUSH_BUTTON,
            LABEL.stop + LABEL.fist:          [OPTION.ACTIVATE_OBJECT, COMMAND.DO],
            LABEL.fist + LABEL.stop:          [OPTION.DEACTIVATE_OBJECT, COMMAND.DO],
            LABEL.thumb_index + LABEL.peace:  OPTION.SLIDER,
        },
        QUESTION.CONNECT: {
            LABEL.thumb_index + LABEL.like:     [OPTION.ENABLE, COMMAND.DO],
            LABEL.thumb_index + LABEL.dislike:  [OPTION.DISABLE, COMMAND.DO],
            LABEL.fist + LABEL.rock:            [OPTION.SELECT,  numerator_connect ],
            LABEL.rock + LABEL.one:             [OPTION.INCREMENT, COMMAND.DO],
            LABEL.rock + LABEL.little_finger:   [OPTION.DECREMENT, COMMAND.DO],
            LABEL.rock + LABEL.stop:            [OPTION.PICK, COMMAND.DO]
        },
        QUESTION.RUNSYS: {
            LABEL.call + LABEL.one:             [HOTKEY_PROGRAM.HOTKEY_RUN_1, OPTION.RUN, COMMAND.DO], ## hot call
            LABEL.call + LABEL.peace:           [HOTKEY_PROGRAM.HOTKEY_RUN_2, OPTION.RUN, COMMAND.DO],
            LABEL.call + LABEL.three:           [HOTKEY_PROGRAM.HOTKEY_RUN_3, OPTION.RUN, COMMAND.DO],
            LABEL.fist + LABEL.rock:            [OPTION.SELECT, literal_programs ],
            LABEL.rock + LABEL.one:             [OPTION.NEXT, COMMAND.DO],
            LABEL.rock + LABEL.little_finger:   [OPTION.PREV, COMMAND.DO],
            LABEL.rock + LABEL.stop:            [OPTION.RUN, COMMAND.DO],       ## run select program
            LABEL.grip + LABEL.like:            [OPTION.RESUME, COMMAND.DO],    ## resume
            LABEL.grip + LABEL.dislike:         [OPTION.STOP, COMMAND.DO],      ## stop
        },
        QUESTION.MOVSYS: {
            LABEL.grip + LABEL.like:            [OPTION.Z_MINUS, COMMAND.DO],
            LABEL.grip + LABEL.dislike:         [OPTION.Z_PLUS,  COMMAND.DO],
            LABEL.grip + LABEL.thumb_index:     [OPTION.X_PLUS, COMMAND.DO],
            LABEL.grip + LABEL.call:            [OPTION.X_MINUS, COMMAND.DO],
            LABEL.grip + LABEL.little_finger:   [OPTION.Y_PLUS, COMMAND.DO],
            LABEL.grip + LABEL.one:             [OPTION.Y_MINUS, COMMAND.DO],
        },
        # QUESTION.CONTROL_PROMPT:{
        #     LABEL.stop + LABEL.fist:           QUESTION.TRASH,
        #     LABEL.star + LABEL.like:           COMMAND.DO,
        #     LABEL.star + LABEL.one:            "&jeden",
        #     LABEL.star + LABEL.peace:          "&dwa",
        #     LABEL.star + LABEL.three:          "&trzy",
        # },
        # QUESTION.STOP: {
        #     LABEL.star + LABEL.star: COMMAND.NONACTION,
        # }
    }

    def compile(self):
        """
           Kompile opoowiada za analize polecen wpisywanych poprzez ruchy rą na podstawie wpisanej przez nie koleji
           wykonywane zostaje akcje odpytań oraz akce DO
        """
        QUESTION = WordCoder.QUESTION
        OPTION  = WordCoder.OPTION
        INFO = WordCoder.INFO
        COMMAND = WordCoder.COMMAND
        DYNAMIC = WordCoder.DYNAMIC

        def _LOG(*args, **kwargs):
            if False:
                print("@", *args, **kwargs)

        def _half_path_in_tree(tree, items, path2elem=None):
            """
                Funkcja odszukuje pierwszą ścieżkę elementów. Ścieżka nie musi byc pełna
            """
            if path2elem is None:  path2elem = []

            for itm in items:
                if itm in tree or itm.__class__ in tree:
                    if isinstance(tree.get(itm), dict):
                        path2elem.append(itm)
                        p2e = path2elem.copy()
                        path2elem = _half_path_in_tree(tree[itm], items, path2elem)
                        if path2elem == None:
                            return p2e
                        break
                    elif isinstance(tree.get(itm.__class__), dict):
                        path2elem.append(itm)
                        p2e = path2elem.copy()
                        path2elem = _half_path_in_tree( tree.get(itm.__class__) , items, path2elem)
                        if path2elem == None:
                            return p2e
                        break
                    else:
                        path2elem.append(itm)
                        break
            else:
                return None
            return path2elem

        def _get_by_path(tree, path2elem):
            node = tree
            for key in path2elem:
                if key in node:
                    node = node.get(key)
                elif key.__class__ in node:
                    node = node.get( key.__class__ )
            return node

        def _GET_CODE():
            """
                Zwrócenie aktualnego statusu kolejki
            """
            return self.queue.get_reverse_buffer()

        def _PUT( *commands ):
            """
                _PUT: word;
                ? funkcja wstawia element na poczatek kolejki
            """
            _LOG(">>_PUT", commands)
            for cmd in commands:
                self.queue.put( cmd )

        def _TRASH( command ):
            """
                TRASH:;
                ? usuwa wszystkie elementy z kolejki
            """
            _LOG(">>TRASH", command)

            ## oczekiwanie na DO które aktywuje proces
            if command == WordCoder.COMMAND.DO:
                ## usuwanie wszysykich elementów
                self.queue.clear()

        def _CLC():
            """
                _CLC:;
                ? ususwa i elemnt z kolejki domyślnie pierwszy
            """
            _LOG(">>_CLC proc",  _GET_CODE())
            CODE = _GET_CODE()
            _TRASH( WordCoder.COMMAND.DO )
            _PUT( *CODE[:-1]  )
            _LOG(">>_CLC end",  _GET_CODE() )

        def NEW( new_question: Sequence[str] ):
            """
                NEW: new_question;

                operator new przenosi wszystko znajduje się w kolejce po konstruktorze

            """
            _LOG( ">>NEW", new_question )

            ## wyczyszenie obecnej koleji
            _TRASH( WordCoder.COMMAND.DO )

            ## ustawiene nowego zapytania
            if isinstance(new_question, str):
                _PUT( new_question )
            elif isinstance(new_question, Sequence):
                _PUT( *new_question )

        def BREAK(ask: Sequence[str]):
            """
                BREAK: question;

                Otrzymuje stan kolejki i wywołuje zamknięcie przedniego zapytania oraz konstruktor nowego zapytania


            """
            assert isinstance(ask, Sequence), TypeError

            index_BREAK = ask.index(WordCoder.COMMAND.BREAK)
            ask: List[str] = list(ask)

            ## przepisanie kolejki z instrukcją zakończenia
            ask_before_break: List[str] = ask[:index_BREAK] + [WordCoder.COMMAND.FINISH]
            ## przygotowanie nowego konstruktora
            ask_after_break: List[str]= ask[index_BREAK + 1:]

            _LOG(">>BREAK:", ask_before_break, "{X}", ask_after_break)
            #IN BREAK
            #wywołania zakończenia zapytania
            if WordCoder.QUESTION.MOV  in ask_before_break:
                MOV(ask_before_break)
            elif WordCoder.QUESTION.INTERACT in ask_before_break:
                INTERACT(ask_before_break)
            elif WordCoder.QUESTION.CONNECT in ask_before_break:
                CONNECT(ask_before_break)
            elif WordCoder.QUESTION.RUNSYS in ask_before_break:
                RUNSYS(ask_before_break)
            else:
                pass
            ## aktualizacja stanu kolejki bez instrukcji wywoływanych przez BREAK
            NEW(ask_after_break)
            self.compile()

        def END(*non):
            """
                END: ;

                Kończy prace odpytania czyści kolejke
            """

            _LOG(">>END")

            ## czyszczenie kolejki
            _TRASH(WordCoder.COMMAND.DO)

        def MOV( commands ): ## BREAK <==============================
            """
                MOV: site-xx, command_move-1 .. command_move-5, DO;

                <?> MOV odpowiada za zarządzanie kolejką zapytania sterowaniem ruchami w aplikacji GUI. Funkcja jest opara
                o założenia ruchowe stawiane w JumpingMachine.

                Załadowanie odpowiedniej składni zapytania uruchamia FLAGE wyzwalającą emisje sygnału do GUI.
            """

            _LOG(">>MOV", commands)

            site_xx = {
                WordCoder.OPTION.SITE_RL: (WordCoder.OPTION.RIGHT, WordCoder.OPTION.LEFT),
                WordCoder.OPTION.SITE_UD: (WordCoder.OPTION.UP, WordCoder.OPTION.DOWN),
                WordCoder.OPTION.SITE_IO: (WordCoder.OPTION.IN, WordCoder.OPTION.OUT),
            }

            ## czyszczenie polecienie w wypadku wyjacia
            if WordCoder.COMMAND.END in commands:
                _TRASH( WordCoder.COMMAND.DO )
                return

            ## dodawanie elementów do move wiąże się z wywołaniem jego konstrukotra w poprawionej formie
            new_ask = [WordCoder.INFO.GUI, WordCoder.QUESTION.MOV]

            ## ustawienie ostatniej nowo dodanej strony
            acctive_site = None
            for cmd in commands:
                if cmd in site_xx.keys(): acctive_site = cmd
            ## jeśli nie ma żadnej strony to wywoływany jest konstruktor
            if acctive_site is not None:
                new_ask.append(acctive_site)

                ## filtracja kierunków ruchu względem aktywnego trybu
                active_direction = []
                for cmd in commands:
                    if cmd in site_xx[acctive_site]:
                        active_direction.append(cmd)
                ## aby ograniczyć zasobność kolejki wprowadzane jest ograniczenie do wyświetlania 5 ostatnich opcji ruchu
                new_ask.extend( active_direction[-4:] )

                ## usunięcie ostatniego elementu, elementy są usuwane aż do site-xx
                if WordCoder.COMMAND.CLC in commands:
                    new_ask.pop(-1)

                ## jeśli istnieją instrukcje ruchowe oraz DO dodawane zostje do kolejki DO
                if active_direction != [] and WordCoder.COMMAND.DO in commands:
                    new_ask.append( WordCoder.COMMAND.DO )

            ## uruchomienie konstruktora kolejki, skasowaenie obecnego stanu i dodanie nowego z przygotowanymi polecaniami
            NEW( new_ask )

            ## pobranie aktualnej kolejki
            code = _GET_CODE()
            index = code.index(WordCoder.QUESTION.MOV)

            ## porawny konstruktor wywołania bedzie miał min 4 element
            if len(code[index:]) >= 4:
                ## aktywacja zapytanie przy pomocy DO
                if WordCoder.COMMAND.DO in code:
                    ## pobranie aktywowanego tagu ruchowego
                    tag: tuple = (WordCoder.QUESTION.MOV, code[-2])
                    ## wyzwalanie sygnału ruchowego
                    self.DATA_emit_SIGNAL_A008 = tag
                    self.FLAG_emit_SIGNAL_A008 = True
                    ## kasowanie DO z kolejki
                    _CLC()
            return

        def INTERACT( commands ):
            """
                INTERACT: object, event, DO:

                <?> INTERACT odpowiada za operowanie elementami w GUI, czyli jest to sposób w jaki użytkownik może operować
                przyciskami, suwakami, itp.

                Załadowanie odpowiedniej składni zapytania uruchamia FLAGE wyzwalającą emisje sygnału do GUI.
            """
            _LOG(">>INTERACT:", commands)

            object_2_interact = {
                WordCoder.OPTION.PUSH_BUTTON: [WordCoder.OPTION.ACTIVATE_OBJECT, WordCoder.OPTION.DEACTIVATE_OBJECT],
            }
            ## dodawanie elementów do move wiąże się z wywołaniem jego konstrukotra w poprawionej formie
            new_ask = [WordCoder.INFO.GUI, WordCoder.QUESTION.INTERACT]

            ## === PRZYGOTOWANIE =======================================================================================

            ## jeśli zawiera end interact to konstruktor został stworzony w nadrzędnym wywołaniu i nie może być ponownie tworzony
            ## dlatego następuje przejście bezpośrednio do aktywacji konstruktora
            if not( WordCoder.COMMAND.FINISH in commands):

                ## ustawienie aktywnego obiektu
                acctive_obiect = None
                for cmd in commands:
                    if cmd in object_2_interact:
                        acctive_obiect = cmd

                ## jeśli nie występują nowe elementy pomijany jest dalszy proces
                if acctive_obiect is not None:
                    new_ask.append( acctive_obiect )

                    # szukanie aktualnej akcji
                    acctive_action = None
                    for cmd in commands:
                        if cmd in object_2_interact[acctive_obiect]:
                            acctive_action = cmd

                    ## jeśli została przypisana odpowiednia akcja do obiektu
                    if acctive_action is not None:
                        new_ask.append(acctive_action)

                        ## jeśli istnieją instrukcje aktywacji oraz DO
                        if WordCoder.COMMAND.DO in commands:
                            new_ask.append( WordCoder.COMMAND.DO )

                    ## uruchomienie konstruktora kolejki, skasowaenie obecnego stanu i dodanie nowego z przygotowanymi polecaniami
                    NEW(new_ask)

                ## pobranie aktualnej kolejki
                code = _GET_CODE()
            else:
                ## inicjacja end iteracjion załoadowanie konstruktora z komend
                new_ask.extend( commands )
                ## kod w przypadku przerwania

            ## === URUCHAMIANIE ========================================================================================

            ## wpisanie zapytania jako kod do okrywacji
            code = new_ask

            _LOG("CODE: ", code)
            index = code.index(WordCoder.QUESTION.INTERACT)

            ## aktywacja gdzy skądnia: INTERACT, object, interaction, ...
            if len(code[index:]) >= 3:
                ## DO akywacha
                if WordCoder.COMMAND.DO in code:
                    tag: str | None = None
                    ## instancja przycisku push
                    if WordCoder.OPTION.PUSH_BUTTON in code:
                        ## dezaktywacja
                        if WordCoder.OPTION.ACTIVATE_OBJECT in code:
                            tag = (WordCoder.QUESTION.INTERACT, WordCoder.OPTION.PUSH_BUTTON, WordCoder.OPTION.ACTIVATE_OBJECT)
                        ## aktywacja
                        elif WordCoder.OPTION.DEACTIVATE_OBJECT in code:
                            tag =  (WordCoder.QUESTION.INTERACT, WordCoder.OPTION.PUSH_BUTTON, WordCoder.OPTION.DEACTIVATE_OBJECT)
                    ## ustawienie kanału sygnału
                    self.DATA_emit_SIGNAL_A008 = tag
                    self.FLAG_emit_SIGNAL_A008 = True
                ## FINISH DO akywacha
                elif WordCoder.COMMAND.FINISH in code:
                    tag: str | None = None
                    ## instancja przycisku push
                    if WordCoder.OPTION.PUSH_BUTTON in code:
                        ## przerwanie powtórzenie dezaktywacji
                        tag = (WordCoder.QUESTION.INTERACT, WordCoder.OPTION.PUSH_BUTTON, WordCoder.OPTION.DEACTIVATE_OBJECT)

                    ## ustawienie kanału sygnału
                    self.DATA_emit_SIGNAL_A008 = tag
                    self.FLAG_emit_SIGNAL_A008 = True

                ## kasowanie DO z kolejki
                _CLC()
            return

        def CONNECT( commands ):
            """
                CONNECT: select :

                connect, able/disable
                select, item

                <?> Oddpytanie opdowiada za zainicjowanie połączenie oraz połaczenie się z jednym z wybranych kontrolerów

                BREAK: -> active
            """


            ### FUNKCJE ================================================================================================

            def patternFunction(func):
                def wrapper(*args, **kwargs):
                    result = func(*args, **kwargs)
                    ## kasowanie DO z kolejki
                    _CLC()
                    return result
                return wrapper

            @patternFunction
            def CallEnable( commands ):
                self.FLAG_emit_SIGNAL_A009 = True
                self.DATA_emit_SIGNAL_A009 = True

            @patternFunction
            def CallDisable( commands ):
                self.FLAG_emit_SIGNAL_A009 = True
                self.DATA_emit_SIGNAL_A009 = False

            @patternFunction
            def CallIncrement( commands ):
                numerator = next(cmd for cmd in commands if isinstance(cmd, DYNAMIC.NUMERATOR))
                numerator.increment()

            @patternFunction
            def CallDecrement( commands ):
                numerator = next(cmd for cmd in commands if isinstance(cmd, DYNAMIC.NUMERATOR))
                numerator.decrement()

            @patternFunction
            def CallPick( commands ):
                numerator = next(cmd for cmd in commands if isinstance(cmd, DYNAMIC.NUMERATOR))

                self.FLAG_emit_SIGNAL_A011 = True
                self.DATA_emit_SIGNAL_A011 = CommunicationTags.WriteComandTags(
                    CommunicationTags.TAG.SELECT_OPTION,
                    numerator.value
                )

            ### STUKTURY WYWOLAN =======================================================================================
            _LOG(">>CONNECT:", commands)

            ## drzewo odpowiadające za poprane zbudowanie zapytania
            tree = {
                OPTION.ENABLE: {
                    COMMAND.DO: CallEnable,
                    COMMAND.FINISH: None,
                },
                OPTION.DISABLE: {
                    COMMAND.DO: CallDisable,
                    COMMAND.FINISH: None,
                },
                OPTION.SELECT:{
                    DYNAMIC.NUMERATOR: {
                        OPTION.PICK: {
                            COMMAND.DO: CallPick,
                            COMMAND.FINISH: None,
                        },
                        OPTION.INCREMENT: {
                            COMMAND.DO: CallIncrement,
                            COMMAND.FINISH: None,
                        },
                        OPTION.DECREMENT: {
                            COMMAND.DO: CallDecrement,
                            COMMAND.FINISH: None,
                        },
                    },
                },
                "3": {
                    "3.1": {
                        "3.1.1": 1,
                        "3.1.2": 2,
                        "3.1.3": 3,
                    },
                    "3.2": {
                        "3.2.1": 1,
                        "3.2.2": 2,
                        "3.2.3": 3,
                    },
                    "3.3": {
                        "3.3.1": 1,
                        "3.3.2": 2,
                        "3.3.3": 3,
                    },
                },
            }

            ## jest to inicjator zapytania odpowiadający gestowi, który go wstawia
            new_ask = [INFO.ROBOT_SERVER, QUESTION.CONNECT]

            ## === PRZYGOTOWANIE =======================================================================================
            """
                Akcja ma na celu zbudowanie poprawnej kolejki odpytania 
            """
            if not (WordCoder.COMMAND.FINISH in commands):
                cmds = commands.copy()
                cmds.reverse()
                new_cmds = _half_path_in_tree(tree, cmds)
                new_ask.extend( new_cmds )
                ## uporządkowanie kolejki
                NEW(new_ask)
            else:
                ## inicjacja FINISH, załoadowanie konstruktora z komend w przypadku finish
                new_ask.extend( commands )

            ## === URUCHAMIANIE ========================================================================================
            """
                Ma na celu wywołanie akcji przypisanej do zestawu komend
            """
            ## odczytanie obecnego kody do wykonania
            code = new_ask

            _LOG("CODE: ", code)
            index = code.index(WordCoder.QUESTION.CONNECT)

            path2func = code[index+1:] ## usuniecie podstawowego new_ask

            func = _get_by_path(tree, path2func)

            if callable(func): func( code )

            return

        def RUNSYS( commands ):
            """
                RUNSYS:

                hotkey, run, do
                select, prog, run, do
                resume, do
                stop, do

                <?> Metoda opowiada za przygotowanie żadań tag-command na server robota,

                BREAK: -> active
            """


            ### FUNKCJE ================================================================================================

            def patternFunction(func):
                def wrapper(*args, **kwargs):
                    result = func(*args, **kwargs)
                    ## kasowanie DO z kolejki
                    _CLC()
                    return result
                return wrapper

            @patternFunction
            def CallNext( commands ):
                literal = next(cmd for cmd in commands if isinstance(cmd, DYNAMIC.LITERAL_LIST))
                literal.next()

            @patternFunction
            def CallPrev( commands ):
                literal = next(cmd for cmd in commands if isinstance(cmd, DYNAMIC.LITERAL_LIST))
                literal.prev()

            @patternFunction
            def CallStop( commands ):
                self.FLAG_emit_SIGNAL_A011 = True
                self.DATA_emit_SIGNAL_A011 = CommunicationTags.WriteComandTags(
                    CommunicationTags.TAG.RUNSYS,
                    CommunicationTags.CMD.STOP
                )

            @patternFunction
            def CallResume(commands):
                self.FLAG_emit_SIGNAL_A011 = True
                self.DATA_emit_SIGNAL_A011 = CommunicationTags.WriteComandTags(
                    CommunicationTags.TAG.RUNSYS,
                    CommunicationTags.CMD.RESUME
                )

            @patternFunction
            def CallRun(commands):

                if any( isinstance( c, WordCoder.DYNAMIC.LITERAL_LIST ) for c in commands ):
                    obj = next(c for c in commands if isinstance(c,  WordCoder.DYNAMIC.LITERAL_LIST))
                    program_name = str(obj)
                elif any( isinstance( c, WordCoder.HOTKEY_PROGRAM) for c in commands ):
                    obj = next(c for c in commands if isinstance(c, WordCoder.HOTKEY_PROGRAM))
                    program_name = obj.value
                else:
                    raise NameError("Problem with program name")

                tc = CommunicationTags.WriteComandTags(
                    CommunicationTags.TAG.RUNSYS,
                    CommunicationTags.CMD.RUN,
                    program_name
                )

                self.FLAG_emit_SIGNAL_A011 = True
                self.DATA_emit_SIGNAL_A011 = tc

            @patternFunction
            def CallNon( commands ):
                _LOG("nono")

            ### STUKTURY WYWOLAN =======================================================================================
            _LOG(">>RUNSYS:", commands)

            ## drzewo odpowiadające za poprane zbudowanie zapytania
            tree = {
                WordCoder.HOTKEY_PROGRAM: {
                    OPTION.RUN: {
                        COMMAND.DO: CallRun,
                        COMMAND.FINISH: None,
                    },
                },
                OPTION.SELECT:{
                    DYNAMIC.LITERAL_LIST: {
                        OPTION.RUN: {
                            COMMAND.DO: CallRun,
                            COMMAND.FINISH: None,
                        },
                        OPTION.NEXT: {
                            COMMAND.DO: CallNext,
                            COMMAND.FINISH: None,
                        },
                        OPTION.PREV: {
                            COMMAND.DO: CallPrev,
                            COMMAND.FINISH: None,
                        },
                    },
                },
                OPTION.RESUME:{
                    COMMAND.DO: CallResume,
                    COMMAND.FINISH: None,
                },
                OPTION.STOP: {
                    COMMAND.DO: CallStop,
                    COMMAND.FINISH: None,
                },
            }

            ## jest to inicjator zapytania odpowiadający gestowi, który go wstawia
            new_ask = [INFO.ROBOT_SERVER, QUESTION.RUNSYS ]

            ## === PRZYGOTOWANIE =======================================================================================
            """
                Akcja ma na celu zbudowanie poprawnej kolejki odpytania 
            """
            if not (COMMAND.FINISH in commands):
                cmds = commands.copy()
                cmds.reverse()
                new_cmds = _half_path_in_tree(tree, cmds)
                new_ask.extend( new_cmds )
                ## uporządkowanie kolejki
                NEW(new_ask)
            else:
                ## inicjacja FINISH, załoadowanie konstruktora z komend w przypadku finish
                new_ask.extend( commands )

            ## === URUCHAMIANIE ========================================================================================
            """
                Ma na celu wywołanie akcji przypisanej do zestawu komend
            """
            ## odczytanie obecnego kody do wykonania
            code = new_ask

            _LOG("CODE: ", code)
            index = code.index(WordCoder.QUESTION.RUNSYS)

            path2func = code[index+1:] ## usuniecie podstawowego new_ask

            func = _get_by_path(tree, path2func)

            if callable(func): func( code )

            return

        def __PATERN(*non):
            """
                _PATERN: non:

                <?> ...

                BREAK: -> active
            """
            _LOG(">>_PATERN:", *non)

            ## drzewo odpowiadające za poprane zbudowanie zapytania
            tree = {
                "1": {
                    "1.1": {
                        "1.1.1": 1,
                        "1.1.2": 2,
                        "1.1.3": 3,
                    },
                    "1.2": {
                        "1.2.1": 1,
                        "1.2.2": 2,
                        "1.2.3": 3,
                    },
                    "1.3": {
                        "1.3.1": 1,
                        "1.3.2": 2,
                        "1.3.3": 3,
                    },
                },
                "2": {
                    "2.1": {
                        "2.1.1": 1,
                        "2.1.2": 2,
                        "2.1.3": 3,
                    },
                    "2.2": {
                        "2.2.1": 1,
                        "2.2.2": 2,
                        "2.2.3": 3,
                    },
                    "2.3": {
                        "2.3.1": 1,
                        "2.3.2": 2,
                        "2.3.3": 3,
                    },
                },
                "3": {
                    "3.1": {
                        "3.1.1": 1,
                        "3.1.2": 2,
                        "3.1.3": 3,
                    },
                    "3.2": {
                        "3.2.1": 1,
                        "3.2.2": 2,
                        "3.2.3": 3,
                    },
                    "3.3": {
                        "3.3.1": 1,
                        "3.3.2": 2,
                        "3.3.3": 3,
                    },
                },
            }

            ## jest to inicjator zapytania odpowiadający gestowi, który go wstawia
            new_ask = [..., ...]

            ## === PRZYGOTOWANIE =======================================================================================
            """
                Akcja ma na celu zbudowanie poprawnej kolejki odpytania 
            """
            if not (WordCoder.COMMAND.FINISH in commands):
                new_cmds = _half_path_in_tree(tree, non)
                new_ask.extend( new_cmds )
                NEW(new_ask)

                some_dict = {}
                ## przeszukiwanie w celu znalezienia ostatniego wystapienia
                active_object = None
                for cmd in commands:
                    if cmd in some_dict:
                        active_object = cmd

                ## ... 1 slowo
                if active_object is not None:

                    new_ask.append(active_object)

                    ## przeszukiwanie w celu znalezienia ostatniego wystapienia
                    active_action = None
                    for cmd in commands:
                        if cmd in some_dict:
                            active_action = cmd

                    ## ... 2 slowo
                    if active_action is not None:
                        new_ask.append(active_action)

                        ## ... 3 slowo
                        if WordCoder.COMMAND.DO in commands:
                            new_ask.append(WordCoder.COMMAND.DO)

                    ## uruchomienie konstruktora kolejki, skasowanie obecnego stanu i dodanie nowego z przygotowanymi polecaniami
                    NEW(new_ask)
            else:
                ## inicjacja FINISH, załoadowanie konstruktora z komend w przypadku finish
                new_ask.extend(commands)

            ## === URUCHAMIANIE ========================================================================================

            ## odczytanie obecnego kody do wykonania
            code = new_ask

            _LOG("CODE: ", code)
            index = code.index(WordCoder.QUESTION.INTERACT)

            ## aktywacja gdzy skądnia: INTERACT, object, interaction, ...
            if len(code[index:]) >= 3:
                ## DO akywacha
                if WordCoder.COMMAND.DO in code:
                    tag: str | None = None
                    ## przesył SINGAL
                    pass
                ## FINISH DO akywacha
                elif WordCoder.COMMAND.FINISH in code:
                    tag: str | None = None
                    ## przesył SINGAL
                    pass
                ## kasowanie DO z kolejki
                _CLC()
            return

        ## ============================================================================================================

        try:
            _LOG("\n\n@compile START ====================================", self.queue)
            code: List[str] = self.queue.get_reverse_buffer()

            if not( set(code).intersection(QUESTION) ):
                ## jesłi kolejka nie zaweira zapytania nie mogą być wstawiane komendy i opcje
                _TRASH(COMMAND.DO)
            # elif WordCoder.QUESTION.CONTROL_PROMPT in code:
            #     # index = code.index(WordCoder.QUESTION.CONTROL_PROMPT)
            #     pass
            #
            elif COMMAND.BREAK in code:
                BREAK( code )
            elif COMMAND.END in code:
                END()
            elif QUESTION.NEW in code:
                ## inicjajca parametrów zapytania
                index = code.index( QUESTION.NEW )
                ## inicjajca parametrów zapytania
                new_question = code[index + 1:]
                NEW(new_question)
            elif QUESTION.MOV in code:
                MOV( code )
            elif QUESTION.INTERACT in code:
                INTERACT( code )
            elif QUESTION.CONNECT in code:
                CONNECT( code )
            elif QUESTION.RUNSYS in code:
                RUNSYS( code )

            _LOG("@compile END =========================================", self.queue)
        except:
            LOG.print(f"<ERR:WordCoder> Compiler Error")


    max_word_in_queue: int = 10

    def __init__(self, task_main:Task , task_command:Task ):

        ## kolejka zapisuje wartości str
        self.queue: CircularBuffer = CircularBuffer(WordCoder.max_word_in_queue)

        self.task_main:Task = task_main
        self.task_command:Task = task_command

        self.acitve_mode_question: str|None = None

        self.refresh_singal_2_basic_statu() ## <- doawanie falg do resetu

    def new_qestion(self, qestions: str):
        ## utworzenie nowego zapytania
        if isinstance(qestions, list):
            for q in qestions:
                self.queue.put(q)
                self.acitve_mode_question = q
        else:
            self.queue.put(qestions)
            self.acitve_mode_question = qestions
        ## rekcja sterego zapytania na nowe
        self.compile()

    def new_command(self, commands: str):
        ## wstawienie komend
        if isinstance(commands, list):
            for cmd in commands:
                self.queue.put(cmd)
        else:
            self.queue.put(commands)
        ## wykonanie kompilacji
        self.compile()

    def check_for_new_status(self):
        ## jeśli wystopił przeskok to następuje dodaniego pytania
        if self.task_main.FLAG_jump_active:
            ## przypisanie komórki danych
            d_y, d_o =  self.task_main.get_data_index(0), self.task_main.get_data_index(1)
            ## odizolowanie przypadku gdy wystąpił brak danych
            if not(d_y == None or d_o == None):
                ## pobranie młodej i starej etykiety klas wyspępujących przy przerwaniu
                lb_y, lb_o = next(iter(d_y.keys())), next(iter(d_o.keys()))
                ## sprawdzenie czy istnieje dla danego przeskoku nowe zapytanie

                ## odpytanie prz przejściu
                question_const2const: str|None = WordCoder.main_hand.get( lb_o+lb_y )

                ## odpytanie prz przejściu
                question_const2star: str | None = WordCoder.main_hand.get(lb_o + WordCoder.LABEL.star)
                ## odpytanie prz przejściu
                question_star2const: str | None = WordCoder.main_hand.get(WordCoder.LABEL.star + lb_y)

                ## odpytanie prz przejściu
                question_star2star: str | None = WordCoder.main_hand.get(WordCoder.LABEL.star + WordCoder.LABEL.star)

                if question_const2const != None:
                    self.new_qestion(question_const2const)
                elif question_const2star != None:
                    self.new_qestion(question_const2star)
                elif question_star2const != None:
                    self.new_qestion(question_star2const)
                elif question_star2star != None:
                    self.new_qestion(question_star2star)
                else:
                    ## nie można określić pytania
                    pass

        ## jeśli wystąpił przeskok to następuje dodanie nowej komędy, oraz gdzy aktywne jest pojawiło sie odpytanie
        if (self.task_command.FLAG_jump_active or self.task_main.FLAG_jump_active) and len(self.queue) > 0:
            ## przypisanie komórki danych
            d_y, d_o = self.task_command.get_data_index(0), self.task_command.get_data_index(1)
            ## odizolowanie przypadku gdy wystąpił brak danych
            if not (d_y == None or d_o == None):
                ## pobranie młodej i starej etykiety klas wyspępujących przy przerwaniu
                lb_y, lb_o = next(iter(d_y.keys())), next(iter(d_o.keys()))
                ## sprawdzenie czy istnieje dla danego przeskoku nowe zapytanie

                ## pobranie zestawu komend dla aktywnego zapytania
                name_question: str = self.acitve_mode_question
                active_question: Dict|None = WordCoder.command_hand.get( name_question )
                ## czy aktywne zapytanie istnieje
                if active_question != None:


                    ## odpytanie prz przejściu
                    command_const2const : str | None = active_question.get( lb_o + lb_y )

                    ## odpytanie prz przejściu
                    command_const2star: str | None = active_question.get(lb_o + WordCoder.LABEL.star)
                    ## odpytanie prz przejściu
                    command_star2const: str | None = active_question.get(WordCoder.LABEL.star + lb_y)

                    ## odpytanie prz przejściu
                    command_star2star: str | None = active_question.get(WordCoder.LABEL.star + WordCoder.LABEL.star)

                    if command_const2const != None:
                        self.new_command(command_const2const)
                    elif command_const2star != None:
                        self.new_command(command_const2star)
                    elif command_star2const != None:
                        self.new_command(command_star2const)
                    elif command_star2star != None:
                        self.new_command(command_star2star)
                    else:
                        ## nie można określić polecenia
                        pass

    def refresh_singal_2_basic_statu(self):
        """
            Po każdym użyciu flag wracać będą do stanu ustawionego w tej metodzie
        """

        ## wysyąłnie tagu MOV
        self.FLAG_emit_SIGNAL_A008: bool = False
        self.DATA_emit_SIGNAL_A008: tuple[str] = None

        self.FLAG_emit_SIGNAL_A009: bool = False
        self.DATA_emit_SIGNAL_A009: bool = False

        self.FLAG_emit_SIGNAL_A011: bool = False
        self.DATA_emit_SIGNAL_A011: T_TagCommand = CommunicationTags.NONTAG

    ## zwraceanie aktywnej kolejki
    def get(self)->Sequence[Any]:
        return self.queue.get_buffer()


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

        E = lambda X, Y: (X if X==Y else 0)
        D = lambda X, Y: (0 if X + Y == 0 else (X or Y)) ## operar or leniwy
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

# class Task:
#     """
#         Task jest strukturą danych posiadającą kolejkie N elementową jako kontener na słowa.
#
#         Dane są przechowwyane w postaci pakietów zawierających nazwę etykiet sprzężoną z czasem trwania wywyołania etykiety.
#     """
#
#     max_data_gesture: int = 5
#
#     def __init__(self, max_word: int = 3, time_limit_ms: int = 8000):
#
#         ## ilosć gestów w kolejce
#         self.max_word = max_word
#         ## kolejka dancyh
#         self.data: CircularBuffer = CircularBuffer(max_word)
#
#         ## maksumalny zakres przetwarzania gestów
#         self.time_limit_ms = time_limit_ms#ms
#
#         # for _ in range(0, max_word+1):
#         ## ustawienie domyślenj 1 wartości kolejki
#         self.data.put({"None": 0})
#
#         ## Flaga określa czy w danej próbce nastąpił przeskok, jest on aktywny do chwili kolejnego sprawdzenia przezskoku
#         self.FLAG_jump_active:bool = False
#
#         ## aktywacja ostaniego słowa
#         self.active_word: str = "None"
#
#     ## ustawienie aktywnego słowa
#     def set_active_word(self, last_word: str):
#         self.active_word: str = last_word
#
#     ## przedluzenie aktywnego gestu
#     def update(self, time_interval_ms: int):
#
#         ## zwiększenie interwału czasowego gestu
#         self.data.first[self.active_word] += time_interval_ms
#
#         ## korekcja kolejki wzlgędem limitu czasu
#         self.fit_to_time_limit(time_interval_ms)
#
#     ## dodanie nowego gestu
#     def new(self, lb: str, time_interval_ms: int):
#         ## wstawienie gestu do kolejki
#         self.data.put( {lb: time_interval_ms} )
#         ## przypisanie ostatniego wstawionego gestu
#         self.set_active_word( lb )
#
#         ## korekcja kolejki wzlgędem limitu czasu
#         self.fit_to_time_limit( time_interval_ms )
#
#     def fit_to_time_limit(self, time_interval_ms:int):
#         """
#             Metoda ma nakładać limit na słowa. Jeśli suma czasów poszczególnych słów jest większa niż zaznaczony limit
#             następuje zminiejszenie wartości ostatniego gesto. Jesli jego wartośc spadnie do minimum zostaje on
#             wyżucony z kolejki.
#         """
#
#         buff: List[Dict[str, int]] = self.data.buffer.copy()
#
#         if len(buff) >= 2:
#             ## Dwa lub więcej gestów w kolejce
#
#             ## zsumowanie czasów poszcególnych gestów
#             complete_time_ms = sum( sum( word.values() ) for word in buff )
#
#             ## analiza przekorzecznia limitu czasowego
#             if complete_time_ms > self.time_limit_ms:
#                 ## pobranie pierwszej i jedynej pary etykieta, czas
#                 lb, time_ms = next(iter(self.data.last.items()))
#
#                 ## zmniejszenie interwału czasowego ostatniego gestu
#                 self.data.last[lb] -= time_interval_ms
#                 ## decycja o usunięciu gestu z kolejki
#                 if time_ms-time_interval_ms <= 0:
#                     self.data.throw()
#         else:
#             ## W kolejce znajduje się tylko jeden gest
#
#             ## pobranie pierwszej i jedynej pary etykieta, czas
#             lb, time_ms = next(iter(self.data.first.items()))
#             ## zablokowanie inkrementu czasowego
#             if time_ms >= self.time_limit_ms:
#                 self.data.first[lb] = self.time_limit_ms
#
#     def get_label(self):
#         return [ next(
#                     iter(d.keys())
#                 )
#                 for d in self.data.get_buffer()
#         ]
#
#     def get_value(self):
#         return [ next(
#                     iter(d.values())
#                 )
#                 for d in self.data.get_buffer()
#         ]
#
#     def get_data(self):
#         return self.data.get_buffer()
#
#     ## zwraca i-ty element Circle Buffer
#     def get_data_index(self, index: int):
#         return self.data.get_buffer_index(index)
#
#     def find_label_contain_time_range(self, t_s:int, t_f:int)-> str:
#         """
#             Fukcja sprawdza czy podany zakres czasowy jest przypisany do pojedyńczej etykiety czasowej
#         """
#         t_c:int = 0 ## poczatek etykiety czasowej
#         t_m:int = -1 ## koniec etykiety czasowej
#         ## ograniczenie do zekresu czasowego
#         if t_f > self.time_limit_ms: t_f = self.time_limit_ms
#
#         ## iteracja po kolejnych etykietach
#         for d in self.data.get_buffer():
#             lb, time = next(iter(d.items()))
#             t_m = time
#             ## sprawdzenie czy szukany zakres znajduje się w jednej etykiecie
#             chk1:bool = t_c <= t_s <= t_m
#             chk2:bool = t_c <= t_f <= t_m
#             ## jesłi jeden znajduje się w zakresie
#             if chk1 or chk2:
#                 ## jeśli dwa znajdują się w zakresise
#                 if chk1 and chk2:
#                     return lb
#                 ## jeśli tylko jeden faktycznie znajduje się w zakresie, przerywane zostaje poszuiwanie
#                 else:
#                     break
#             else:
#                 ## zwiekszenie dolnego zakresu o rozmiar obecnej etykiety
#                 t_c += t_m
#                 continue
#         ## zwrot ogólnej etykiety
#         return "None"
#
#     def __str__(self):
#         return "<task>: " + str(self.data)


# class CellularAutomaton:
#     """
#         Automat posiada wektor wejściowy 9 próbek, na ich podstawie zwraca wekro adekwatnej długości zapewniajacy na
#         okreslenie przejścia między grupami. Automat może zwrócić wektor reprezentujący do 3 grup.
#
#         Podczas pracy wykonywane są następujące kryteria:
#             1. "Dominacją strony" Na każde z 9 próbek przypada 1 wektor analizy, który sprawdza sąsiedztwo do 2 próbek.
#             Jeśli któraś ze stron posiada wartość dominującą to nadpisuje ona wartośc próbki.
#
#             2. "Dominacja względem próbki" Jeśli 2 strony posiadają wartość dominująca,
#             następuje nadpisanie zgodnie z wartościa próbki (zgodna wartość próbki powoduje pozostawienie wartości próbki).
#
#             3. "Dominacja względem środka" Jeśli natomiast próbka nie decydyje o wyniku sprawdzana jest pozycja próbki
#             względem środka wektora. Wybrana zostaje strona bliższa środkowi
#
#             4. "Trwałość dziur granicznych" Jeśli na 5 granicznych próbkach zwyłaczeniem skrajnej próbki powstała dziura
#             na 4 próbki (wartości 0) to wartości tych próbek nie mogą zostać nadpisane.
#     """
#
#     def __init__(self, Q: Sequence[int]):
#         """
#             Inicjacja warunków poczatkowych automatu.
#         """
#         self.Q_0 =  np.array(Q)
#         self.Q_state: List[Sequence] = [self.Q_0]
#
#     def run(self):
#         """
#             Uruchomienie automatu do czasu osiągnięcia stabilności układu.
#         """
#         Q_last = self.Q_0
#         Q = self.Q_0
#
#         while True:
#             Q = self.next_state( Q )
#             if np.array_equal(Q, Q_last) :
#                 break
#             else:
#                 Q_last = Q
#
#         return Q_last
#
#     def next_state(self, Q_t: Sequence[int])->Sequence[int]:
#         """
#             Iteracja jednego przejścia automatu komórkowego
#         """
#
#         Q_t = np.array(Q_t)
#
#         V = np.concatenate([[-1, -1], Q_t, [-1, -1]])
#
#         T = np.row_stack([V[n:n + 5] for n in range(0, 9)])
#
#         U = []
#         for trr in T:
#             urr = []
#             for t in trr:
#                 if t == -1:
#                     urr.append(trr[2])
#                 else:
#                     urr.append(t)
#             U.append(np.array(urr))
#         U = np.array(U)
#
#         E = lambda X, Y: (X if X==Y else 0)
#         D = lambda X, Y: (0 if X + Y == 0 else (X or Y))
#         C = lambda X, Y: (X or Y)
#
#         W = []
#         X = []
#         Z = []
#         Y = []
#         for urr in U:
#             wrr = []
#             xrr = []
#             zrr = []
#             yrr = []
#
#             wrr.append(E(urr[0], urr[1]))
#             wrr.append(urr[2])
#             wrr.append(E(urr[3], urr[4]))
#
#             xrr.append(E(wrr[0], wrr[1]))
#             xrr.append(E(wrr[1], wrr[2]))
#
#             zrr.append(C(xrr[0], xrr[1]))
#
#             yrr.append(D(wrr[0], wrr[2]))
#             yrr.append(D(wrr[2], wrr[0]))
#
#             W.append(wrr)
#             X.append(xrr)
#             Z.append(zrr)
#             Y.append(yrr)
#
#         W = np.array(W)
#         X = np.array(X)
#         Z = np.array(Z)
#         Y = np.array(Y)
#
#         Q_tp1 = []
#         for i, (zrr, yrr) in enumerate(zip(Z, Y)):
#             if zrr[0] != 0:
#                 Q_tp1.append(zrr[0])
#             else:
#                 s = 1 if i < len(Q_t) / 2 else 0
#                 Q_tp1.append(yrr[s])
#
#         Q_tp1 = np.array(Q_tp1)
#         if np.all(Q_t[1:5] == 0):
#             Q_tp1[1:5] = 0
#         if np.all(Q_t[4:8] == 0):
#             Q_tp1[4:8] = 0
#
#         return Q_tp1
#
#
# # noinspection PyTypeChecker
# class WordCoder:
#
#     class LABEL(str, Enum):
#         """
#             KLasa reprezentuje etykiery kodowania, zgodne z etykietami gestów. Klasa ma również 2 dodatkowe elementy
#             star reprezentująca dowolny gest,oraz non reprezentująca brak gestu.
#         """
#         call = "call"
#         dislike = "dislike"
#         fist = "fist"
#         grip = "grip"
#         like = "like"
#         little_finger = "little_finger"
#         one = "one"
#         peace = "peace"
#         rock = "rock"
#         stop = "stop"
#         three = "three"
#         three3 = "three3"
#         thumb_index = "thumb_index"
#         non = "None"
#         star = "*"
#
#     class INFO(str, Enum):
#         GUI = "GUI"
#         ROBOT_SERVER = "ROBOT-SERVER"
#
#     class QUESTION(str, Enum):
#         NEW = "NEW"
#         ##
#         MOV = "MOV"
#         INTERACT = "INTERACT"
#         ##
#         CONNECT = "CONNECT"
#
#         CONTROL_PROMPT = ">>"
#
#         STOP = "STOP" # not use
#
#     class COMMAND(str, Enum):
#         DO = "DO"
#         CLC = "CLC"
#         END = "END" ## ma za zadanie zakończyć prace obecnego odpytania i wyczyści kolejkę
#         BREAK = "BREAK" ## przerywa obecne odpytanie, ale pozostawia nowy stan odpytania
#         FINISH = "FINISH" ## dodany do kolejki odpowiada za przerwanie w zapytania
#
#     class OPTION(str, Enum):
#         ## opcje MOV
#         SITE_RL = "SITE_RL"
#         SITE_UD = "SITE_UD"
#         SITE_IO = "SITE_IO"
#         LEFT = "LEFT"
#         RIGHT = "RIGHT"
#         UP = "UP"
#         DOWN = "DOWN"
#         IN = "IN"
#         OUT = "OUT"
#         ## ITERACT
#         SELECT = "SELECT"
#         PUSH_BUTTON = "PUSH_BUTTON"
#         ACTIVATE_OBJECT = "ACTIVATE_OBJECT"
#         DEACTIVATE_OBJECT = "DEACTIVATE_OBJECT"
#         END_INTERACT = "END_INTERACT"
#         ## CONNECT
#         ENABLE = "ENABLE"
#         DISABLE = "DISABLE"
#         # SELECT = ...
#         INCREMENT = "INCREMENT"
#         DECREMENT = "DECREMENT"
#         PICK = "PICK"
#
#     class DYNAMIC:
#         class SelfStrDrawMethaClass(type):
#             def __str__(cls) -> str: return str(cls.value)
#
#         class NUMERATOR(metaclass=SelfStrDrawMethaClass):
#             def __init__(self, value=0, range_=5):
#                 self.value = value
#                 self.range = range_
#
#             def increment(self):
#                 self.value += 1
#                 if self.value > self.range:
#                     self.value = 0
#
#             def decrement(self):
#                 self.value -= 1
#                 if self.value < 0:
#                     self.value = self.range
#
#             def __str__(self):
#                 return str(self.value)
#
#
#     main_hand = { ## Aby aktywować zasobnik command_hand na końcu powinno być przypisane odpowiednie przekierowanie
#         LABEL.stop + LABEL.rock: [ QUESTION.NEW, INFO.GUI, QUESTION.MOV ],
#         LABEL.rock + LABEL.star: [ COMMAND.END ],
#         LABEL.stop + LABEL.one:  [ QUESTION.NEW, INFO.GUI, QUESTION.INTERACT ],
#         LABEL.one  + LABEL.star: [ COMMAND.BREAK ],
#         LABEL.stop + LABEL.grip: [ QUESTION.NEW, INFO.ROBOT_SERVER, QUESTION.CONNECT ],
#         LABEL.grip + LABEL.star: [ COMMAND.END ],
#         # LABEL.star + LABEL.call: QUESTION.CONTROL_PROMPT,
#         # LABEL.star + LABEL.call: COMMAND.END
#         # LABEL.rock + LABEL.star: QUESTION.TRASH,
#         # LABEL.star + LABEL.one:  QUESTION.INTERACT,
#         # LABEL.star + LABEL.fist: QUESTION.TRASH
#     }
#     command_hand = {
#         QUESTION.MOV: {
#             LABEL.star + LABEL.like:          [OPTION.SITE_RL, OPTION.RIGHT, COMMAND.DO],
#             LABEL.star + LABEL.thumb_index:   [OPTION.SITE_RL, OPTION.LEFT, COMMAND.DO],
#             LABEL.star + LABEL.rock:          OPTION.SITE_UD,
#             LABEL.rock + LABEL.three3:        [OPTION.UP, COMMAND.DO],
#             LABEL.rock + LABEL.little_finger: [OPTION.DOWN, COMMAND.DO],
#             LABEL.fist + LABEL.stop:           OPTION.SITE_IO,
#             LABEL.stop + LABEL.one:           [OPTION.IN, COMMAND.DO],
#             LABEL.stop + LABEL.peace:         [OPTION.OUT, COMMAND.DO],
#             LABEL.call + LABEL.like:          [COMMAND.DO],
#             LABEL.call + LABEL.dislike:       [COMMAND.CLC],
#         },
#         QUESTION.INTERACT: {
#             LABEL.star + LABEL.thumb_index:   [COMMAND.BREAK,  QUESTION.NEW, INFO.GUI, QUESTION.INTERACT, OPTION.SELECT],
#             LABEL.thumb_index + LABEL.one:    OPTION.PUSH_BUTTON,
#             LABEL.stop + LABEL.fist:          [OPTION.ACTIVATE_OBJECT, COMMAND.DO],
#             LABEL.fist + LABEL.stop:          [OPTION.DEACTIVATE_OBJECT, COMMAND.DO],
#         },
#         QUESTION.CONNECT: {
#             LABEL.thumb_index + LABEL.like:     [OPTION.ENABLE, COMMAND.DO],
#             LABEL.thumb_index + LABEL.dislike:  [OPTION.DISABLE, COMMAND.DO],
#             LABEL.fist + LABEL.rock:            [OPTION.SELECT, DYNAMIC.NUMERATOR(3, 10) ],
#             LABEL.rock + LABEL.one:             [OPTION.INCREMENT, COMMAND.DO],
#             LABEL.rock + LABEL.little_finger:   [OPTION.DECREMENT, COMMAND.DO],
#             LABEL.rock + LABEL.stop:            [OPTION.PICK, COMMAND.DO]
#         },
#         # QUESTION.CONTROL_PROMPT:{
#         #     LABEL.stop + LABEL.fist:           QUESTION.TRASH,
#         #     LABEL.star + LABEL.like:           COMMAND.DO,
#         #     LABEL.star + LABEL.one:            "&jeden",
#         #     LABEL.star + LABEL.peace:          "&dwa",
#         #     LABEL.star + LABEL.three:          "&trzy",
#         # },
#         # QUESTION.STOP: {
#         #     LABEL.star + LABEL.star: COMMAND.NONACTION,
#         # }
#     }
#
#     def compile(self):
#         """
#            Kompile opoowiada za analize polecen wpisywanych poprzez ruchy rą na podstawie wpisanej przez nie koleji
#            wykonywane zostaje akcje odpytań oraz akce DO
#         """
#         QUESTION = WordCoder.QUESTION
#         OPTION  = WordCoder.OPTION
#         INFO = WordCoder.INFO
#         COMMAND = WordCoder.COMMAND
#         DYNAMIC = WordCoder.DYNAMIC
#
#         def _half_path_in_tree(tree, items, path2elem=None):
#             """
#                 Funkcja odszukuje pierwszą ścieżkę elementów. Ścieżka nie musi byc pełna
#             """
#             if path2elem is None:  path2elem = []
#
#             for itm in items:
#                 if itm in tree or itm.__class__ in tree:
#                     if isinstance(tree.get(itm), dict):
#                         path2elem.append(itm)
#                         p2e = path2elem.copy()
#                         path2elem = _half_path_in_tree(tree[itm], items, path2elem)
#                         if path2elem == None:
#                             return p2e
#                         break
#                     elif isinstance(tree.get(itm.__class__), dict):
#                         path2elem.append(itm)
#                         p2e = path2elem.copy()
#                         path2elem = _half_path_in_tree( tree.get(itm.__class__) , items, path2elem)
#                         if path2elem == None:
#                             return p2e
#                         break
#                     else:
#                         path2elem.append(itm)
#                         break
#             else:
#                 return None
#             return path2elem
#
#         def _get_by_path(tree, path2elem):
#             node = tree
#             for key in path2elem:
#                 if key in node:
#                     node = node.get(key)
#                 elif key.__class__ in node:
#                     node = node.get( key.__class__ )
#             return node
#
#         def _GET_CODE():
#             """
#                 Zwrócenie aktualnego statusu kolejki
#             """
#             return self.queue.get_reverse_buffer()
#
#         def _PUT( *commands ):
#             """
#                 _PUT: word;
#                 ? funkcja wstawia element na poczatek kolejki
#             """
#             print(">>_PUT", commands)
#             for cmd in commands:
#                 self.queue.put( cmd )
#
#         def _TRASH( command ):
#             """
#                 TRASH:;
#                 ? usuwa wszystkie elementy z kolejki
#             """
#             print(">>TRASH", command)
#
#             ## oczekiwanie na DO które aktywuje proces
#             if command == WordCoder.COMMAND.DO:
#                 ## usuwanie wszysykich elementów
#                 self.queue.clear()
#
#         def _CLC():
#             """
#                 _CLC:;
#                 ? ususwa i elemnt z kolejki domyślnie pierwszy
#             """
#             print(">>_CLC proc",  _GET_CODE())
#             CODE = _GET_CODE()
#             _TRASH( WordCoder.COMMAND.DO )
#             _PUT( *CODE[:-1]  )
#             print(">>_CLC end",  _GET_CODE() )
#
#         def NEW( new_question: Sequence[str] ):
#             """
#                 NEW: new_question;
#
#                 operator new przenosi wszystko znajduje się w kolejce po konstruktorze
#
#             """
#             print( ">>NEW", new_question )
#
#             ## wyczyszenie obecnej koleji
#             _TRASH( WordCoder.COMMAND.DO )
#
#             ## ustawiene nowego zapytania
#             if isinstance(new_question, str):
#                 _PUT( new_question )
#             elif isinstance(new_question, Sequence):
#                 _PUT( *new_question )
#
#         def BREAK(ask: Sequence[str]):
#             """
#                 BREAK: question;
#
#                 Otrzymuje stan kolejki i wywołuje zamknięcie przedniego zapytania oraz konstruktor nowego zapytania
#
#
#             """
#             assert isinstance(ask, Sequence), TypeError
#
#             index_BREAK = ask.index(WordCoder.COMMAND.BREAK)
#             ask: List[str] = list(ask)
#
#             ## przepisanie kolejki z instrukcją zakończenia
#             ask_before_break: List[str] = ask[:index_BREAK] + [WordCoder.COMMAND.FINISH]
#             ## przygotowanie nowego konstruktora
#             ask_after_break: List[str]= ask[index_BREAK + 1:]
#
#             print(">>BREAK:", ask_before_break, "{X}", ask_after_break)
#             #IN BREAK
#             #wywołania zakończenia zapytania
#             if WordCoder.QUESTION.MOV  in ask_before_break:
#                 MOV(ask_before_break)
#             elif WordCoder.QUESTION.INTERACT in ask_before_break:
#                 INTERACT(ask_before_break)
#             elif WordCoder.QUESTION.CONNECT in ask_before_break:
#                 CONNECT(ask_before_break)
#             else:
#                 pass
#             ## aktualizacja stanu kolejki bez instrukcji wywoływanych przez BREAK
#             NEW(ask_after_break)
#             self.compile()
#
#         def END(*non):
#             """
#                 END: ;
#
#                 Kończy prace odpytania czyści kolejke
#             """
#
#             print(">>END")
#
#             ## czyszczenie kolejki
#             _TRASH(WordCoder.COMMAND.DO)
#
#         def MOV( commands ): ## BREAK <==============================
#             """
#                 MOV: site-xx, command_move-1 .. command_move-5, DO;
#
#                 <?> MOV odpowiada za zarządzanie kolejką zapytania sterowaniem ruchami w aplikacji GUI. Funkcja jest opara
#                 o założenia ruchowe stawiane w JumpingMachine.
#
#                 Załadowanie odpowiedniej składni zapytania uruchamia FLAGE wyzwalającą emisje sygnału do GUI.
#             """
#
#             print(">>MOV", commands)
#
#             site_xx = {
#                 WordCoder.OPTION.SITE_RL: (WordCoder.OPTION.RIGHT, WordCoder.OPTION.LEFT),
#                 WordCoder.OPTION.SITE_UD: (WordCoder.OPTION.UP, WordCoder.OPTION.DOWN),
#                 WordCoder.OPTION.SITE_IO: (WordCoder.OPTION.IN, WordCoder.OPTION.OUT),
#             }
#
#             ## czyszczenie polecienie w wypadku wyjacia
#             if WordCoder.COMMAND.END in commands:
#                 _TRASH( WordCoder.COMMAND.DO )
#                 return
#
#             ## dodawanie elementów do move wiąże się z wywołaniem jego konstrukotra w poprawionej formie
#             new_ask = [WordCoder.INFO.GUI, WordCoder.QUESTION.MOV]
#
#             ## ustawienie ostatniej nowo dodanej strony
#             acctive_site = None
#             for cmd in commands:
#                 if cmd in site_xx.keys(): acctive_site = cmd
#             ## jeśli nie ma żadnej strony to wywoływany jest konstruktor
#             if acctive_site is not None:
#                 new_ask.append(acctive_site)
#
#                 ## filtracja kierunków ruchu względem aktywnego trybu
#                 active_direction = []
#                 for cmd in commands:
#                     if cmd in site_xx[acctive_site]:
#                         active_direction.append(cmd)
#                 ## aby ograniczyć zasobność kolejki wprowadzane jest ograniczenie do wyświetlania 5 ostatnich opcji ruchu
#                 new_ask.extend( active_direction[-4:] )
#
#                 ## usunięcie ostatniego elementu, elementy są usuwane aż do site-xx
#                 if WordCoder.COMMAND.CLC in commands:
#                     new_ask.pop(-1)
#
#                 ## jeśli istnieją instrukcje ruchowe oraz DO dodawane zostje do kolejki DO
#                 if active_direction != [] and WordCoder.COMMAND.DO in commands:
#                     new_ask.append( WordCoder.COMMAND.DO )
#
#             ## uruchomienie konstruktora kolejki, skasowaenie obecnego stanu i dodanie nowego z przygotowanymi polecaniami
#             NEW( new_ask )
#
#             ## pobranie aktualnej kolejki
#             code = _GET_CODE()
#             index = code.index(WordCoder.QUESTION.MOV)
#
#             ## porawny konstruktor wywołania bedzie miał min 4 element
#             if len(code[index:]) >= 4:
#                 ## aktywacja zapytanie przy pomocy DO
#                 if WordCoder.COMMAND.DO in code:
#                     ## pobranie aktywowanego tagu ruchowego
#                     tag: tuple = (WordCoder.QUESTION.MOV, code[-2])
#                     ## wyzwalanie sygnału ruchowego
#                     self.DATA_emit_SIGNAL_A008 = tag
#                     self.FLAG_emit_SIGNAL_A008 = True
#                     ## kasowanie DO z kolejki
#                     _CLC()
#             return
#
#         def INTERACT( commands ):
#             """
#                 INTERACT: object, event, DO:
#
#                 <?> INTERACT odpowiada za operowanie elementami w GUI, czyli jest to sposób w jaki użytkownik może operować
#                 przyciskami, suwakami, itp.
#
#                 Załadowanie odpowiedniej składni zapytania uruchamia FLAGE wyzwalającą emisje sygnału do GUI.
#             """
#             print(">>INTERACT:", commands)
#
#             object_2_interact = {
#                 WordCoder.OPTION.PUSH_BUTTON: [WordCoder.OPTION.ACTIVATE_OBJECT, WordCoder.OPTION.DEACTIVATE_OBJECT],
#             }
#             ## dodawanie elementów do move wiąże się z wywołaniem jego konstrukotra w poprawionej formie
#             new_ask = [WordCoder.INFO.GUI, WordCoder.QUESTION.INTERACT]
#
#             ## === PRZYGOTOWANIE =======================================================================================
#
#             ## jeśli zawiera end interact to konstruktor został stworzony w nadrzędnym wywołaniu i nie może być ponownie tworzony
#             ## dlatego następuje przejście bezpośrednio do aktywacji konstruktora
#             if not( WordCoder.COMMAND.FINISH in commands):
#
#                 ## ustawienie aktywnego obiektu
#                 acctive_obiect = None
#                 for cmd in commands:
#                     if cmd in object_2_interact:
#                         acctive_obiect = cmd
#
#                 ## jeśli nie występują nowe elementy pomijany jest dalszy proces
#                 if acctive_obiect is not None:
#                     new_ask.append( acctive_obiect )
#
#                     # szukanie aktualnej akcji
#                     acctive_action = None
#                     for cmd in commands:
#                         if cmd in object_2_interact[acctive_obiect]:
#                             acctive_action = cmd
#
#                     ## jeśli została przypisana odpowiednia akcja do obiektu
#                     if acctive_action is not None:
#                         new_ask.append(acctive_action)
#
#                         ## jeśli istnieją instrukcje aktywacji oraz DO
#                         if WordCoder.COMMAND.DO in commands:
#                             new_ask.append( WordCoder.COMMAND.DO )
#
#                     ## uruchomienie konstruktora kolejki, skasowaenie obecnego stanu i dodanie nowego z przygotowanymi polecaniami
#                     NEW(new_ask)
#
#                 ## pobranie aktualnej kolejki
#                 code = _GET_CODE()
#             else:
#                 ## inicjacja end iteracjion załoadowanie konstruktora z komend
#                 new_ask.extend( commands )
#                 ## kod w przypadku przerwania
#
#             ## === URUCHAMIANIE ========================================================================================
#
#             ## wpisanie zapytania jako kod do okrywacji
#             code = new_ask
#
#             print("CODE: ", code)
#             index = code.index(WordCoder.QUESTION.INTERACT)
#
#             ## aktywacja gdzy skądnia: INTERACT, object, interaction, ...
#             if len(code[index:]) >= 3:
#                 ## DO akywacha
#                 if WordCoder.COMMAND.DO in code:
#                     tag: str | None = None
#                     ## instancja przycisku push
#                     if WordCoder.OPTION.PUSH_BUTTON in code:
#                         ## dezaktywacja
#                         if WordCoder.OPTION.ACTIVATE_OBJECT in code:
#                             tag = (WordCoder.QUESTION.INTERACT, WordCoder.OPTION.PUSH_BUTTON, WordCoder.OPTION.ACTIVATE_OBJECT)
#                         ## aktywacja
#                         elif WordCoder.OPTION.DEACTIVATE_OBJECT in code:
#                             tag =  (WordCoder.QUESTION.INTERACT, WordCoder.OPTION.PUSH_BUTTON, WordCoder.OPTION.DEACTIVATE_OBJECT)
#                     ## ustawienie kanału sygnału
#                     self.DATA_emit_SIGNAL_A008 = tag
#                     self.FLAG_emit_SIGNAL_A008 = True
#                 ## FINISH DO akywacha
#                 elif WordCoder.COMMAND.FINISH in code:
#                     tag: str | None = None
#                     ## instancja przycisku push
#                     if WordCoder.OPTION.PUSH_BUTTON in code:
#                         ## przerwanie powtórzenie dezaktywacji
#                         tag = (WordCoder.QUESTION.INTERACT, WordCoder.OPTION.PUSH_BUTTON, WordCoder.OPTION.DEACTIVATE_OBJECT)
#
#                     ## ustawienie kanału sygnału
#                     self.DATA_emit_SIGNAL_A008 = tag
#                     self.FLAG_emit_SIGNAL_A008 = True
#
#                 ## kasowanie DO z kolejki
#                 _CLC()
#             return
#
#         def CONNECT( commands ):
#             """
#                 CONNECT: select :
#
#                 connect, able/disable
#                 select, item
#
#                 <?> Oddpytanie opdowiada za zainicjowanie połączenie oraz połaczenie się z jednym z wybranych kontrolerów
#
#                 BREAK: -> active
#             """
#
#
#             ### FUNKCJE ================================================================================================
#
#             def patternFunction(func):
#                 def wrapper(*args, **kwargs):
#                     result = func(*args, **kwargs)
#                     ## kasowanie DO z kolejki
#                     _CLC()
#                     return result
#                 return wrapper
#
#             @patternFunction
#             def CallEnable( commands ):
#                 self.FLAG_emit_SIGNAL_A009 = True
#                 self.DATA_emit_SIGNAL_A009 = True
#
#             @patternFunction
#             def CallDisable( commands ):
#                 self.FLAG_emit_SIGNAL_A009 = True
#                 self.DATA_emit_SIGNAL_A009 = False
#
#             @patternFunction
#             def CallIncrement( commands ):
#                 numerator = next(cmd for cmd in commands if isinstance(cmd, DYNAMIC.NUMERATOR))
#                 numerator.increment()
#
#             @patternFunction
#             def CallDecrement( commands ):
#                 numerator = next(cmd for cmd in commands if isinstance(cmd, DYNAMIC.NUMERATOR))
#                 numerator.decrement()
#
#             @patternFunction
#             def CallPick( commands ):
#                 numerator = next(cmd for cmd in commands if isinstance(cmd, DYNAMIC.NUMERATOR))
#
#                 self.FLAG_emit_SIGNAL_A011 = True
#                 self.DATA_emit_SIGNAL_A011 = CommunicationTags.WriteComandTags(
#                     CommunicationTags.TAG.SELECT_OPTION,
#                     numerator.value
#                 )
#
#             ### STUKTURY WYWOLAN =======================================================================================
#             print(">>CONNECT:", commands)
#
#             ## drzewo odpowiadające za poprane zbudowanie zapytania
#             tree = {
#                 OPTION.ENABLE: {
#                     COMMAND.DO: CallEnable,
#                     COMMAND.FINISH: None,
#                 },
#                 OPTION.DISABLE: {
#                     COMMAND.DO: CallDisable,
#                     COMMAND.FINISH: None,
#                 },
#                 OPTION.SELECT:{
#                     DYNAMIC.NUMERATOR: {
#                         OPTION.PICK: {
#                             COMMAND.DO: "None5",
#                             COMMAND.FINISH: None,
#                         },
#                         OPTION.INCREMENT: {
#                             COMMAND.DO: CallIncrement,
#                             COMMAND.FINISH: None,
#                         },
#                         OPTION.DECREMENT: {
#                             COMMAND.DO: CallIncrement,
#                             COMMAND.FINISH: None,
#                         },
#                     },
#                 },
#                 "3": {
#                     "3.1": {
#                         "3.1.1": 1,
#                         "3.1.2": 2,
#                         "3.1.3": 3,
#                     },
#                     "3.2": {
#                         "3.2.1": 1,
#                         "3.2.2": 2,
#                         "3.2.3": 3,
#                     },
#                     "3.3": {
#                         "3.3.1": 1,
#                         "3.3.2": 2,
#                         "3.3.3": 3,
#                     },
#                 },
#             }
#
#             ## jest to inicjator zapytania odpowiadający gestowi, który go wstawia
#             new_ask = [INFO.ROBOT_SERVER, QUESTION.CONNECT]
#
#             ## === PRZYGOTOWANIE =======================================================================================
#             """
#                 Akcja ma na celu zbudowanie poprawnej kolejki odpytania
#             """
#             if not (WordCoder.COMMAND.FINISH in commands):
#                 cmds = commands.copy()
#                 cmds.reverse()
#                 new_cmds = _half_path_in_tree(tree, cmds)
#                 new_ask.extend( new_cmds )
#                 ## uporządkowanie kolejki
#                 NEW(new_ask)
#             else:
#                 ## inicjacja FINISH, załoadowanie konstruktora z komend w przypadku finish
#                 new_ask.extend( commands )
#
#             ## === URUCHAMIANIE ========================================================================================
#             """
#                 Ma na celu wywołanie akcji przypisanej do zestawu komend
#             """
#             ## odczytanie obecnego kody do wykonania
#             code = new_ask
#
#             print("CODE: ", code)
#             index = code.index(WordCoder.QUESTION.CONNECT)
#
#             path2func = code[index+1:] ## usuniecie podstawowego new_ask
#
#             func = _get_by_path(tree, path2func)
#
#             if callable(func): func( code )
#
#             return
#
#         def __PATERN(*non):
#             """
#                 _PATERN: non:
#
#                 <?> ...
#
#                 BREAK: -> active
#             """
#             print(">>_PATERN:", *non)
#
#             ## drzewo odpowiadające za poprane zbudowanie zapytania
#             tree = {
#                 "1": {
#                     "1.1": {
#                         "1.1.1": 1,
#                         "1.1.2": 2,
#                         "1.1.3": 3,
#                     },
#                     "1.2": {
#                         "1.2.1": 1,
#                         "1.2.2": 2,
#                         "1.2.3": 3,
#                     },
#                     "1.3": {
#                         "1.3.1": 1,
#                         "1.3.2": 2,
#                         "1.3.3": 3,
#                     },
#                 },
#                 "2": {
#                     "2.1": {
#                         "2.1.1": 1,
#                         "2.1.2": 2,
#                         "2.1.3": 3,
#                     },
#                     "2.2": {
#                         "2.2.1": 1,
#                         "2.2.2": 2,
#                         "2.2.3": 3,
#                     },
#                     "2.3": {
#                         "2.3.1": 1,
#                         "2.3.2": 2,
#                         "2.3.3": 3,
#                     },
#                 },
#                 "3": {
#                     "3.1": {
#                         "3.1.1": 1,
#                         "3.1.2": 2,
#                         "3.1.3": 3,
#                     },
#                     "3.2": {
#                         "3.2.1": 1,
#                         "3.2.2": 2,
#                         "3.2.3": 3,
#                     },
#                     "3.3": {
#                         "3.3.1": 1,
#                         "3.3.2": 2,
#                         "3.3.3": 3,
#                     },
#                 },
#             }
#
#             ## jest to inicjator zapytania odpowiadający gestowi, który go wstawia
#             new_ask = [..., ...]
#
#             ## === PRZYGOTOWANIE =======================================================================================
#             """
#                 Akcja ma na celu zbudowanie poprawnej kolejki odpytania
#             """
#             if not (WordCoder.COMMAND.FINISH in commands):
#                 new_cmds = _half_path_in_tree(tree, non)
#                 new_ask.extend( new_cmds )
#                 NEW(new_ask)
#
#                 some_dict = {}
#                 ## przeszukiwanie w celu znalezienia ostatniego wystapienia
#                 active_object = None
#                 for cmd in commands:
#                     if cmd in some_dict:
#                         active_object = cmd
#
#                 ## ... 1 slowo
#                 if active_object is not None:
#
#                     new_ask.append(active_object)
#
#                     ## przeszukiwanie w celu znalezienia ostatniego wystapienia
#                     active_action = None
#                     for cmd in commands:
#                         if cmd in some_dict:
#                             active_action = cmd
#
#                     ## ... 2 slowo
#                     if active_action is not None:
#                         new_ask.append(active_action)
#
#                         ## ... 3 slowo
#                         if WordCoder.COMMAND.DO in commands:
#                             new_ask.append(WordCoder.COMMAND.DO)
#
#                     ## uruchomienie konstruktora kolejki, skasowanie obecnego stanu i dodanie nowego z przygotowanymi polecaniami
#                     NEW(new_ask)
#             else:
#                 ## inicjacja FINISH, załoadowanie konstruktora z komend w przypadku finish
#                 new_ask.extend(commands)
#
#             ## === URUCHAMIANIE ========================================================================================
#
#             ## odczytanie obecnego kody do wykonania
#             code = new_ask
#
#             print("CODE: ", code)
#             index = code.index(WordCoder.QUESTION.INTERACT)
#
#             ## aktywacja gdzy skądnia: INTERACT, object, interaction, ...
#             if len(code[index:]) >= 3:
#                 ## DO akywacha
#                 if WordCoder.COMMAND.DO in code:
#                     tag: str | None = None
#                     ## przesył SINGAL
#                     pass
#                 ## FINISH DO akywacha
#                 elif WordCoder.COMMAND.FINISH in code:
#                     tag: str | None = None
#                     ## przesył SINGAL
#                     pass
#                 ## kasowanie DO z kolejki
#                 _CLC()
#             return
#
#         ## ============================================================================================================
#
#         print("\n\n@compile START ====================================", self.queue)
#         code: List[str] = self.queue.get_reverse_buffer()
#
#         if not( set(code).intersection(QUESTION) ):
#             ## jesłi kolejka nie zaweira zapytania nie mogą być wstawiane komendy i opcje
#             _TRASH(COMMAND.DO)
#         # elif WordCoder.QUESTION.CONTROL_PROMPT in code:
#         #     # index = code.index(WordCoder.QUESTION.CONTROL_PROMPT)
#         #     pass
#         #
#         elif COMMAND.BREAK in code:
#             BREAK( code )
#         elif COMMAND.END in code:
#             END()
#         elif QUESTION.NEW in code:
#             ## inicjajca parametrów zapytania
#             index = code.index( QUESTION.NEW )
#             ## inicjajca parametrów zapytania
#             new_question = code[index + 1:]
#             NEW(new_question)
#         elif QUESTION.MOV in code:
#             MOV( code )
#         elif QUESTION.INTERACT in code:
#             INTERACT( code )
#         elif QUESTION.CONNECT in code:
#             CONNECT( code )
#
#         print("@compile END =========================================", self.queue)
#
#
#     max_word_in_queue: int = 10
#
#     def __init__(self, task_main:Task , task_command:Task ):
#
#         ## kolejka zapisuje wartości str
#         self.queue: CircularBuffer = CircularBuffer(WordCoder.max_word_in_queue)
#
#         self.task_main:Task = task_main
#         self.task_command:Task = task_command
#
#         self.acitve_mode_question: str|None = None
#
#         self.refresh_singal_2_basic_statu() ## <- doawanie falg do resetu
#
#     def new_qestion(self, qestions: str):
#         ## utworzenie nowego zapytania
#         if isinstance(qestions, list):
#             for q in qestions:
#                 self.queue.put(q)
#                 self.acitve_mode_question = q
#         else:
#             self.queue.put(qestions)
#             self.acitve_mode_question = qestions
#         ## rekcja sterego zapytania na nowe
#         self.compile()
#
#     def new_command(self, commands: str):
#         ## wstawienie komend
#         if isinstance(commands, list):
#             for cmd in commands:
#                 self.queue.put(cmd)
#         else:
#             self.queue.put(commands)
#         ## wykonanie kompilacji
#         self.compile()
#
#     def check_for_new_status(self):
#         ## jeśli wystopił przeskok to następuje dodaniego pytania
#         if self.task_main.FLAG_jump_active:
#             ## przypisanie komórki danych
#             d_y, d_o =  self.task_main.get_data_index(0), self.task_main.get_data_index(1)
#             ## odizolowanie przypadku gdy wystąpił brak danych
#             if not(d_y == None or d_o == None):
#                 ## pobranie młodej i starej etykiety klas wyspępujących przy przerwaniu
#                 lb_y, lb_o = next(iter(d_y.keys())), next(iter(d_o.keys()))
#                 ## sprawdzenie czy istnieje dla danego przeskoku nowe zapytanie
#
#                 ## odpytanie prz przejściu
#                 question_const2const: str|None = WordCoder.main_hand.get( lb_o+lb_y )
#
#                 ## odpytanie prz przejściu
#                 question_const2star: str | None = WordCoder.main_hand.get(lb_o + WordCoder.LABEL.star)
#                 ## odpytanie prz przejściu
#                 question_star2const: str | None = WordCoder.main_hand.get(WordCoder.LABEL.star + lb_y)
#
#                 ## odpytanie prz przejściu
#                 question_star2star: str | None = WordCoder.main_hand.get(WordCoder.LABEL.star + WordCoder.LABEL.star)
#
#                 if question_const2const != None:
#                     self.new_qestion(question_const2const)
#                 elif question_const2star != None:
#                     self.new_qestion(question_const2star)
#                 elif question_star2const != None:
#                     self.new_qestion(question_star2const)
#                 elif question_star2star != None:
#                     self.new_qestion(question_star2star)
#                 else:
#                     ## nie można określić pytania
#                     pass
#
#         ## jeśli wystąpił przeskok to następuje dodanie nowej komędy, oraz gdzy aktywne jest pojawiło sie odpytanie
#         if (self.task_command.FLAG_jump_active or self.task_main.FLAG_jump_active) and len(self.queue) > 0:
#             ## przypisanie komórki danych
#             d_y, d_o = self.task_command.get_data_index(0), self.task_command.get_data_index(1)
#             ## odizolowanie przypadku gdy wystąpił brak danych
#             if not (d_y == None or d_o == None):
#                 ## pobranie młodej i starej etykiety klas wyspępujących przy przerwaniu
#                 lb_y, lb_o = next(iter(d_y.keys())), next(iter(d_o.keys()))
#                 ## sprawdzenie czy istnieje dla danego przeskoku nowe zapytanie
#
#                 ## pobranie zestawu komend dla aktywnego zapytania
#                 name_question: str = self.acitve_mode_question
#                 active_question: Dict|None = WordCoder.command_hand.get( name_question )
#                 ## czy aktywne zapytanie istnieje
#                 if active_question != None:
#
#
#                     ## odpytanie prz przejściu
#                     command_const2const : str | None = active_question.get( lb_o + lb_y )
#
#                     ## odpytanie prz przejściu
#                     command_const2star: str | None = active_question.get(lb_o + WordCoder.LABEL.star)
#                     ## odpytanie prz przejściu
#                     command_star2const: str | None = active_question.get(WordCoder.LABEL.star + lb_y)
#
#                     ## odpytanie prz przejściu
#                     command_star2star: str | None = active_question.get(WordCoder.LABEL.star + WordCoder.LABEL.star)
#
#                     if command_const2const != None:
#                         self.new_command(command_const2const)
#                     elif command_const2star != None:
#                         self.new_command(command_const2star)
#                     elif command_star2const != None:
#                         self.new_command(command_star2const)
#                     elif command_star2star != None:
#                         self.new_command(command_star2star)
#                     else:
#                         ## nie można określić polecenia
#                         pass
#
#     def refresh_singal_2_basic_statu(self):
#         """
#             Po każdym użyciu flag wracać będą do stanu ustawionego w tej metodzie
#         """
#
#         ## wysyąłnie tagu MOV
#         self.FLAG_emit_SIGNAL_A008: bool = False
#         self.DATA_emit_SIGNAL_A008: tuple[str] = None
#
#         self.FLAG_emit_SIGNAL_A009: bool = False
#         self.DATA_emit_SIGNAL_A009: bool = False
#
#         self.FLAG_emit_SIGNAL_A011: bool = False
#         self.DATA_emit_SIGNAL_A011: T_TagCommand = CommunicationTags.NONTAG
#
#     ## zwraceanie aktywnej kolejki
#     def get(self)->Sequence[Any]:
#         return self.queue.get_buffer()