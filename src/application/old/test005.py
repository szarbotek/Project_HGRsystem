

class JumpingMachine:

    FLAG_IsConnectionGenerate: bool = False

    border_line_thickness: int = 4
    color_border_active: QColor = QColor(255, 0, 0)
    color_border_inactive: QColor = QColor(0, 0, 0)

    max_layer: int = 6

    colors_for_layer: Tuple[QColor, ...] = (
        QColor(255, 87, 34),
        QColor(0, 230, 118),
        QColor(41, 121, 255),
        QColor(255, 234, 0),
        QColor(213, 0, 249),
        QColor(0, 229, 255)
    )

    layer_index: int
    ID: int = 0
    created_object: Set['JumpingMachine'] = set()
    movement_courser: 'JumpingMachine' = None

    @classmethod
    def setIDnLayer(cls, subject) -> None:
        """
            Ustawienie unikalnego ID dla nowego obiektu, oraz numeru warswy na bazie rodzica.
            Dodatkowo dla pierwszego elementu ustawiany zostaje kursor.

        :param subject: obiekt klasy JumpingMachine, który wywołuje methode
        :type subject: JumpingMachine
        :return:
        :rtype: None
        """
        subject.ID = cls.ID
        cls.ID += 1
        cls.created_object.add(subject)

        if subject.ID == 0:
            subject.layer_index = 0

            # ustawienie kursora
            cls.setMovementCursor(subject)
        else:
            assert subject.parent.layer_index < cls.max_layer, ValueError(" Maximum layer Exceeded ")
            subject.layer_index = subject.parent.layer_index + 1

    @classmethod
    def setMovementCursor(cls, subject):
        prev = cls.movement_courser

        cls.movement_courser = subject
        cls.movement_courser.FLAG_IsObjectSelected = True
        cls.movement_courser.update()

        if isinstance(prev, JumpingMachine):
            prev.FLAG_IsObjectSelected = False
            prev.update()

    @classmethod
    def genetateConnections(cls):

        def setConnectOfAllObjInSpecificSection(subjectGrupe: List[JumpingMachine | QWidget]) -> None:
            """
                Fukncja dla każdego elementu z grupy ustawia 6 połaczeń

                Bazowe ustawienia dla obiektu:
                subject.connection: Dict[str, Union[JumpingMachine, None] ] = {
                    'W': None, 'S': None, 'A': None, 'D': None,
                    'IN': None, 'OUT': None,}

            :param subjectGrupe:
            :type subjectGrupe: List[JumpingMachine|QWidget]
            :return:
            :rtype: None
            """

            def findMinToSideXY(subject, searchSub, typeXY: str, modeLR: str) -> JumpingMachine:
                """
                    Funkcja ma na celu znalezienie najblirzej połorzonego obiektu,
                    wzgledem danego boku instacji JumpingMachine

                :param subject: obiekt wzgledem którego następuje przeszukanie
                :param searchSub: grupa obiektów w sekcji bez elementy wzglednego
                :param side:
                :return:
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
                if len(arr_obj) <= 2: return arr_obj[-1]

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

            # znalezienie najbardziej min(x,y) obiektu dla rodzica dla mechanizmu wchodzenia
            outdrop: JumpingMachine = None

            # przejdzie po sekcji grupy bedacej wycinkiem warstwy
            for subject in subjectGrupe:
                if isinstance(subject.parent, JumpingMachine):  subject.connection["OUT"] = subject.parent

                # szukanie połaczenia do wchodzenia
                if outdrop == None:
                    outdrop = subject
                else:
                    # miniumum Y
                    if subject.sideW < outdrop.sideW:
                        outdrop = subject
                    # minimum X
                    elif (subject.sideW == outdrop.sideW and subject.sideA < outdrop.sideA):
                        outdrop: outdrop = subject

                searchSub: List[JumpingMachine | QWidget] = subjectGrupe.copy()
                searchSub.remove(subject)

                if len(searchSub) == 0:
                    continue
                else:
                    subject.connection["W"] = findMinToSideXY(subject, searchSub, "Y", "L")
                    subject.connection["S"] = findMinToSideXY(subject, searchSub, "Y", "R")

                    subject.connection["A"] = findMinToSideXY(subject, searchSub, "X", "L")
                    subject.connection["D"] = findMinToSideXY(subject, searchSub, "X", "R")
            else:
                if isinstance(outdrop.parent, JumpingMachine): outdrop.parent.connection['IN'] = outdrop

        segments_per_parent: Dict[JumpingMachine, List[JumpingMachine]] = dict()

        # podział obiektów na segmenty
        for obj in cls.created_object:
            obj: JumpingMachine | QWidget

            # wyznaczenie charakterystycznych boków dla poszczególnych obiektow
            obj.sideW: int = obj.y()
            obj.sideS: int = obj.y() + obj.height()
            obj.sideA: int = obj.x()
            obj.sideD: int = obj.x() + obj.width()

            if obj.parent in segments_per_parent.keys():
                segments_per_parent[obj.parent].append(obj)
            else:
                segments_per_parent[obj.parent] = [obj]

        for parent, children in segments_per_parent.items(): setConnectOfAllObjInSpecificSection(children)

        """ === LOG ================================================================================================ """
        print("\n[LOG] created connection in aplication")
        for obj in cls.created_object:
            print("..", obj, obj.connection["W"], obj.connection["S"], obj.connection["A"], obj.connection["D"],
                obj.connection["IN"], obj.connection["OUT"])

        cls.FLAG_IsConnectionGenerate = True

    def __init__(self, parentJP=None, instanceJP=None):
        self.frame = Frame( parentJP, instanceJP )

        self.ID: int
        self.layer_index: int
        # fagi
        self.FLAG_IsObjectSelected = False

        self.parent: JumpingMachine = parentJP

        # ustawienie indeksu ID oraz warstwy
        JumpingMachine.setIDnLayer(self)

        self.colorfill: QColor = JumpingMachine.colors_for_layer[self.layer_index]

        self.sideW: int = 0
        self.sideS: int = 0
        self.sideA: int = 0
        self.sideD: int = 0

        # mapa połaczeń przskoków do kolejnych obiektów
        self.connection: Dict[str, Union[JumpingMachine, None]] = {
            'W': None, 'S': None, 'A': None, 'D': None,
            'IN': None, 'OUT': None,
        }

        print("<< Creat JumpingMachine: ID", self.ID, "parent", self.parent, "layer", self.layer_index)

    @classmethod
    def genetateConnections(cls):

        def setConnectOfAllObjInSpecificSection(subjectGrupe: List[JumpingMachine | QWidget]) -> None:
            """
                Fukncja dla każdego elementu z grupy ustawia 6 połaczeń

                Bazowe ustawienia dla obiektu:
                subject.connection: Dict[str, Union[JumpingMachine, None] ] = {
                    'W': None, 'S': None, 'A': None, 'D': None,
                    'IN': None, 'OUT': None,}

            :param subjectGrupe:
            :type subjectGrupe: List[JumpingMachine|QWidget]
            :return:
            :rtype: None
            """

            def findMinToSideXY(subject, searchSub, typeXY: str, modeLR: str) -> JumpingMachine:
                """
                    Funkcja ma na celu znalezienie najblirzej połorzonego obiektu,
                    wzgledem danego boku instacji JumpingMachine

                :param subject: obiekt wzgledem którego następuje przeszukanie
                :param searchSub: grupa obiektów w sekcji bez elementy wzglednego
                :param side:
                :return:
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
                if len(arr_obj) <= 2: return arr_obj[-1]

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

            # znalezienie najbardziej min(x,y) obiektu dla rodzica dla mechanizmu wchodzenia
            outdrop: JumpingMachine = None

            # przejdzie po sekcji grupy bedacej wycinkiem warstwy
            for subject in subjectGrupe:
                if isinstance(subject.parent, JumpingMachine):  subject.connection["OUT"] = subject.parent

                # szukanie połaczenia do wchodzenia
                if outdrop == None:
                    outdrop = subject
                else:
                    # miniumum Y
                    if subject.sideW < outdrop.sideW:
                        outdrop = subject
                    # minimum X
                    elif (subject.sideW == outdrop.sideW and subject.sideA < outdrop.sideA):
                        outdrop: outdrop = subject

                searchSub: List[JumpingMachine | QWidget] = subjectGrupe.copy()
                searchSub.remove(subject)

                if len(searchSub) == 0:
                    continue
                else:
                    subject.connection["W"] = findMinToSideXY(subject, searchSub, "Y", "L")
                    subject.connection["S"] = findMinToSideXY(subject, searchSub, "Y", "R")

                    subject.connection["A"] = findMinToSideXY(subject, searchSub, "X", "L")
                    subject.connection["D"] = findMinToSideXY(subject, searchSub, "X", "R")
            else:
                if isinstance(outdrop.parent, JumpingMachine): outdrop.parent.connection['IN'] = outdrop

        segments_per_parent: Dict[JumpingMachine, List[JumpingMachine]] = dict()

        # podział obiektów na segmenty
        for obj in cls.created_object:
            obj: JumpingMachine | QWidget

            # wyznaczenie charakterystycznych boków dla poszczególnych obiektow
            obj.sideW: int = obj.y()
            obj.sideS: int = obj.y() + obj.height()
            obj.sideA: int = obj.x()
            obj.sideD: int = obj.x() + obj.width()

            if obj.parent in segments_per_parent.keys():
                segments_per_parent[obj.parent].append(obj)
            else:
                segments_per_parent[obj.parent] = [obj]

        for parent, children in segments_per_parent.items(): setConnectOfAllObjInSpecificSection(children)

        """ === LOG ================================================================================================ """
        print("\n[LOG] created connection in aplication")
        for obj in cls.created_object:
            print("..", obj, obj.connection["W"], obj.connection["S"], obj.connection["A"], obj.connection["D"],
                  obj.connection["IN"], obj.connection["OUT"])

        cls.FLAG_IsConnectionGenerate = True

    def jump(self, direction: str):

        if direction in self.connection.keys():
            subject = self.connection[direction]
            print(" Press : ...", direction)
            if isinstance(subject, JumpingMachine):
                print(" MOVE TO : ...", subject)
                JumpingMachine.setMovementCursor(subject)
            else:
                pass
        else:
            pass

    def __str__(self) -> str:
        return "<JumpingMachine: {}>".format(self.ID)
