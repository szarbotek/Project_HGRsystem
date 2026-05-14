from PyQt5.QtWidgets import QWidget, QMainWindow, QPushButton
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen
from PyQt5.QtCore import Qt

from typing import List, Tuple, Set, Dict, Union
from collections.abc import Callable

# class Frame(QWidget):
#     """
#         Klasa frame towrzy obiekt pod QWigetem do którego należy, który symuluje efekt aktywnej ramki
#
#     """
#
#     thickness: int = 1
#
#     frames_instances: List = []
#
#     color_mode: Dict[bool, QColor] = {
#         False: QColor(0,0,0),
#         True:  QColor(255,0,0),
#     }
#
#     @classmethod
#     def fit_size(cls):
#         """
#             Funkcja poprawia instacje do których przypisane są ramki
#
#         """
#         th = cls.thickness
#
#         frr = cls.frames_instances.copy()
#
#         for fi in frr:
#             x, y = fi.pos().x(), fi.pos().y()
#             w, h = fi.width(), fi.height()
#
#             ff = th
#             ff2 = 2*ff
#             pd = fi.layer_index * ff2
#
#             fi.setGeometry(x+ff, y+ff, w-pd-ff2, h-pd-ff2)
#             x, y = fi.pos().x(), fi.pos().y()
#             w, h = fi.width(), fi.height()
#
#     def __init__(self, parent=None, instance=None):
#         QWidget.__init__(self, parent)
#
#         # sprawszenie czy instancja do kótej podpięta jest ramka dziedziczy po JumpingMachine
#         assert isinstance(instance, JumpingMachine), TypeError
#
#         Frame.frames_instances.append(instance)
#
#         self.instance = instance
#
#         self.border_thickness = Frame.thickness
#         self.border_color = QColor(0, 0, 0)
#
#     def paintEvent(self, event):
#         try:
#             x, y = self.instance.pos().x(), self.instance.pos().y()
#             painter = QPainter(self)
#
#             # Włączenie wygładzania krawędzi
#             painter.setRenderHint(QPainter.Antialiasing)
#
#             color = Frame.color_mode[self.instance.FLAG_is_object_selected]
#
#             painter.setBrush(QBrush(color, Qt.SolidPattern))
#             painter.setPen(Qt.NoPen)
#
#             W = self.instance.width() + 2 * self.border_thickness
#             H = self.instance.height() + 2 * self.border_thickness
#
#             self.move(x - self.border_thickness, y - self.border_thickness)
#             self.resize(W, H)
#             self.stackUnder( self.instance )
#
#             # Rysowanie zaokrąglonego prostokąta (np. promień 10px)
#             painter.drawRoundedRect(0, 0, W, H, 10.0, 10.0)
#
#         except Exception as e:
#             print(e)
#
#

class JumpingMachine:
    """
        Clasa łaczy się z elementem QWiget tworzac do niego instancjie ramki.
        Spośród wszystkich instancji jedna stanowi kursor, który pozwala na poruszanie się pomiędzy warstwami, oraz
        QWiget umiejscowionumi na tym samym poziomie warstwy. Poziom warstw jest określony poprez obiekt Parent i tak
        opiekty o tej samej instancji znajdują się w tej samej warstwie.

        Opiektem wyjściowym jest QMainWindow, a elementem kocowym obiekty instacji JP*

    """

    layer_index: int
    layer_max_index: int = 6
    ID: int = 0
    active_instance_of_class: Set['JumpingMachine'] = set()

    @classmethod
    def set_ID(cls, subject):
        """
            Ustawienie unikalnego ID dla nowego obiektu, oraz numeru warswy na bazie rodzica.
            Dodatkowo dla pierwszego elementu ustawiany zostaje kursor.

        :param subject: obiekt klasy JumpingMachine, który wywołuje methode
        :type subject: JumpingMachine
        """

        subject.ID = cls.ID
        cls.ID += 1
        cls.active_instance_of_class.add( subject )

        if isinstance(subject.parent, QMainWindow):
            subject.layer_index = 0
        else:
            # odziolowanie przypadku gdy następuje próba nadanai indexu dla obiektów ponad QMainWindow
            assert subject.parent.layer_index < cls.layer_max_index, ValueError(" Maximum layer Exceeded ")

            # ustawienie aktywnej warstwy opiektu
            subject.layer_index = subject.parent.layer_index + 1

    movement_courser: 'JumpingMachine' = None

    @classmethod
    def set_cursor(cls, subject: 'JumpingMachine'):
        """
            Swaping kursora między akrywnym frame a adekwatnym do wywołania connection
        """

        prev = cls.movement_courser

        cls.movement_courser = subject
        cls.movement_courser.FLAG_is_object_selected = True
        cls.movement_courser.update()

        if isinstance(prev, JumpingMachine):
            prev.FLAG_is_object_selected = False
            prev.update()

    FLAG_is_connection_generate: bool = False

    @classmethod
    def generate_connetion(cls):
        """
            Fukncja dla każdego elementu z grupy ustawia 6 połaczeń

            Bazowe ustawienia dla obiektu:
            subject.connection: Dict[str, Union[JumpingMachine, None] ] = {
                'W': None, 'S': None, 'A': None, 'D': None,
                'IN': None, 'OUT': None,}

        :param subjectGrupe:
        :type subjectGrupe: List[JumpingMachine|QWidget]
        """

        def creat_connection_of_all_object_in_section( sectionParent:JumpingMachine | QWidget, sectionChildren: List[JumpingMachine | QWidget]  )-> None:

            def find_min_to_side_XY(subject, searchSub, typeXY: str, modeLR: str) -> JumpingMachine:
                """
                    Funkcja ma na celu znalezienie najblirzej połorzonego obiektu,
                    wzgledem danego boku instacji JumpingMachine

                :param subject: obiekt wzgledem którego następuje przeszukanie
                :param searchSub: grupa obiektów w sekcji bez elementy wzglednego
                :param typeXY: analiza względem osi X lyb Y
                :param modeLR: analiza względem strony L lub R
                """


                # buffor dla obiektów
                arr_obj: List[JumpingMachine | QWidget | None] = [None]

                # FAZA 1, znalezeienie wszystkich obiektów po danej stronie:
                for sub in searchSub:
                    sub: JumpingMachine
                    if typeXY == "Y":
                        if modeLR == "L":
                            if subject.sideW > sub.sideW or subject.sideW > sub.sideS: arr_obj.append(sub)
                        elif modeLR == "R":
                            if subject.sideS < sub.sideW or subject.sideS < sub.sideS: arr_obj.append(sub)
                    elif typeXY == "X":
                        if modeLR == "L":
                            if subject.sideA > sub.sideA or subject.sideA > sub.sideD: arr_obj.append(sub)
                        elif modeLR == "R":
                            if subject.sideD < sub.sideA or subject.sideD < sub.sideD: arr_obj.append(sub)

                print("F1..", subject, typeXY, modeLR, *arr_obj)

                # jeśli zostały znalezione tylko 2 obiekty gdzie jeden to domyślne None wtedy można zwrócić przeszukanie
                if len(arr_obj) <= 2:
                    return arr_obj[-1]

                brr_obj: List[JumpingMachine | QWidget | None] = [None]

                # FAZA 2, zawężenie zakresu względem prostopadłych boków:
                for sub in arr_obj[1:]:
                    sub: JumpingMachine
                    if typeXY == "Y":
                        if (subject.sideA <= sub.sideA < subject.sideD or
                                subject.sideA < sub.sideD <= subject.sideD): brr_obj.append(sub)
                    elif typeXY == "X":
                        if (subject.sideW <= sub.sideW < subject.sideS or
                                subject.sideW < sub.sideS <= subject.sideS): brr_obj.append(sub)

                print("F2..", subject, typeXY, modeLR, *brr_obj)

                if len(brr_obj) == 1:
                    # zawęrzenie wykluczyło obiekty należy znaleć najbardziej skrajny ale bez zwerzenia
                    brr_obj = arr_obj
                elif len(brr_obj) == 2:
                    # jeden przypadek
                    return brr_obj[-1]
                else:
                    # znaleziono wiecej obiektów nalezy znaleźc najblirzszy i i taki ze skrajnym wektorem
                    pass

                # FAZA 3, znalezienie obiektu w minimalnej odległosci od sub:
                # gdzie dodatakowym warunkeim jest posaidanie mniejszych (x,y)
                extreme_case = None
                for sub in brr_obj[1:]:
                    if extreme_case == None:
                        extreme_case = sub
                        continue
                    extreme_case: JumpingMachine

                    if typeXY == "Y":
                        if modeLR == "L":
                            if extreme_case.sideS < sub.sideS:
                                extreme_case = sub
                            elif (extreme_case.sideS == sub.sideS and extreme_case.sideA > sub.sideA):
                                extreme_case = sub
                        elif modeLR == "R":
                            if extreme_case.sideW > sub.sideW:
                                extreme_case = sub
                            elif (extreme_case.sideW == sub.sideW and extreme_case.sideA > sub.sideA):
                                extreme_case = sub
                    elif typeXY == "X":
                        if modeLR == "L":
                            if extreme_case.sideD < sub.sideD:
                                extreme_case = sub
                            elif (extreme_case.sideD == sub.sideD and extreme_case.sideW > sub.sideW):
                                extreme_case = sub
                        elif modeLR == "R":
                            if extreme_case.sideA > sub.sideA:
                                extreme_case = sub
                            elif (extreme_case.sideA == sub.sideA and extreme_case.sideW > sub.sideW):
                                extreme_case = sub

                print("F3..", subject, typeXY, modeLR, extreme_case)
                return extreme_case

                pass
            # znalezienie najbardziej min(x,y) obiektu dla rodzica dla mechanizmu wchodzenia
            outdrop: JumpingMachine = None

            for subject in sectionChildren:

                #ustawienie obiektu nadrzędnego wyjściowego
                if isinstance(subject.parent, JumpingMachine):
                    subject.map_connection["OUT"] = subject.parent

                if outdrop == None:
                    outdrop = subject
                else:
                    # miniumum Y, czy element doąży do górnego lewego rogu
                    if subject.sideW < outdrop.sideW:
                        outdrop = subject
                    # minimum X, czy element doąży do górnego lewego rogu
                    elif (subject.sideW == outdrop.sideW and subject.sideA < outdrop.sideA):
                        outdrop: outdrop = subject

                searchSub: List[JumpingMachine | QWidget] = sectionChildren.copy()
                searchSub.remove(subject)

                if len(searchSub) != 0:
                    subject.map_connection["W"] = find_min_to_side_XY(subject, searchSub, "Y", "L")
                    subject.map_connection["S"] = find_min_to_side_XY(subject, searchSub, "Y", "R")

                    subject.map_connection["A"] = find_min_to_side_XY(subject, searchSub, "X", "L")
                    subject.map_connection["D"] = find_min_to_side_XY(subject, searchSub, "X", "R")

            else:
                # ustawienie obiektu wejścowego wewnętrznego
                if isinstance(outdrop.parent, JumpingMachine):
                    outdrop.parent.map_connection['IN'] = outdrop


        segments_per_parent: Dict[JumpingMachine, List[JumpingMachine]] = dict()

        for obj in cls.active_instance_of_class:
            print( obj.x(), obj.y(), obj.width(), obj.height() )
            # wyznaczenie charakterystycznych boków dla poszczególnych obiektow
            obj.sideA: int = obj.x()
            obj.sideD: int = obj.x() + obj.width()
            obj.sideW: int = obj.y()
            obj.sideS: int = obj.y() + obj.height()

            if obj.parent in segments_per_parent.keys():
                segments_per_parent[obj.parent].append(obj)
            else:
                segments_per_parent[obj.parent] = [obj]

            print(obj.parent)

        print( segments_per_parent )

        for parent, children in segments_per_parent.items():
            creat_connection_of_all_object_in_section( parent, children )


        cls.FLAG_is_connection_generate = True

    @classmethod
    def refresh_button(cls):
        for subject in cls.active_instance_of_class:
            print( "$$$", subject, isinstance(subject, QPushButton) )
            if isinstance(subject, QPushButton): subject.map_connection["IN"] = subject.click

    def __init__(self, parentJP=None, instanceJP=None):

        # instacnjca ramki przypisana do obiektu, ramki nie są klasyfikowane do JumpingMachine
        # self.frame = Frame( parentJP, instanceJP )

        # aktywator podświetlanie ramki
        self.FLAG_is_object_selected = False

        self.parent: JumpingMachine | QWidget | None = parentJP

        # ustawienie unikalnego adresu ID
        JumpingMachine.set_ID(self)

        # mapa połaczeń przskoków do kolejnych obiektów
        self.map_connection: Dict[str, Union[JumpingMachine, None]] = {
            'W': None, 'S': None, 'A': None, 'D': None,
            'IN': None, 'OUT': None,
        }

        print("<< Creat JumpingMachine: ID", self.ID, "parent", self.parent, "layer", self.layer_index)

    def jump(self, move_tag):

        print("<< Jump >>", move_tag, self)

        if move_tag in self.map_connection.keys():

            if move_tag == "IN":
                if isinstance(self.map_connection[move_tag], Callable):
                    self.map_connection[move_tag]()

            subject = self.map_connection[move_tag]

            if isinstance(subject, JumpingMachine):
                JumpingMachine.set_cursor( subject )