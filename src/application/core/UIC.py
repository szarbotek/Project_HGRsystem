"""
    User interface Controler.

    Jest to wątek odpowiedzialny za sterowanie.

    W tym celu na hand_landmark zostaje dokonana klasyfikacja po normalizacji przy użyciu klasyfikatora przygotowanego
    specjalne pod zestaw danych. Gesty są gromadzone w 2 taskach po jednym dla każdej dłoni. W przypadku realizacji komendy
    wysyłały zostaje odpowiedni komunikat.

"""

from src.application.utils.HandGastureControlSystem import *

from PyQt5.QtCore import QThread, pyqtSignal, QTimer

from sklearn.preprocessing import LabelEncoder

from data.project_values import LOG, FALG_NORMALIZATION
from src.func.special import MODEL_H5, NPY
from src.func.analyzing_tool import normalization, landmark2array
from src.application.utils.structure import T_LeftRight, CircularBuffer

from typing import List, Tuple
from src.application.utils.ComunicationProtocol import T_TagCommand, T_DictionaryMessage

import numpy as np

import traceback

import time

class CentralUnitThread(QThread):

    ###
    SIGNAL_A004_2GUI = pyqtSignal( list, list ) ## przesył listy wykrytych próbek
    SIGNAL_A005_2GUI = pyqtSignal( list, list )  ## przesył buffora etykiet Tasków jako 2 Listy
    SIGNAL_A006_2GUI = pyqtSignal(list, list)  ## przesył buffora czasów Tasków jako 2 Listy
    SIGNAL_A007_2GUI = pyqtSignal( list )  ## kolejka WordKodera
    SIGNAL_A008_2GUI = pyqtSignal( object ) ## odpytanie ruchu MOV
    SIGNAL_A009_2CMT = pyqtSignal( bool ) ## aktywacja/dezaktywacja połączenia
    ###
    SIGNAL_A011_2CMT = pyqtSignal( str )
    SIGNAL_A012_2GUI = pyqtSignal( object )

    def SIGNAL_A003_4MPR(self, *args):
        try:
            ## sprawdzenie struktury przesyłu danych
            assert len(args) == 2, IndexError
            ## zapsianie danych klatki do Wigetu odpowiedzialnego za wyswietlanie
            ts = args[0]
            landmarks = args[1]
            self.data_to_gesture_prediction.append( (ts, landmarks) )
        except Exception as e:
            LOG.print(f"<ERR> SIGNAL_A003_4MPR: {e}, {args}")

    def SIGNAL_A010_4CMT(self, info: Tuple[T_TagCommand, T_DictionaryMessage] ):
        try:
            tag, msg = info
            ### przesłanie sygnału do gui
            self.SIGNAL_A012_2GUI.emit( (tag, msg) )

            if tag == CommunicationTags.TAG.MESSAGE:
                ## odczyt stanu kontrolera
                self.data_unit = msg.get(CommunicationTags.MessageDictKeys.dataUnit)
            elif tag == CommunicationTags.TAG.CONTROL:
                self.control = msg
                ## uaktualnienie listy dostępnych programów
                programs: Dict[str, str] = msg.get( CommunicationTags.MessageDictKeys.programs )
                self.word_coder.literal_programs.setup( 0, list(programs.keys()) )
            elif tag == CommunicationTags.TAG.CONFIGURATE:
                ## uaktualnienie stanu wyboru kontrolerów
                self.configurate = msg
                controllers: Dict[str, Any] = msg.get( CommunicationTags.MessageDictKeys.controllers )
                self.word_coder.numerator_connect.setup( 0, len(controllers) )

        except Exception as e:
            LOG.print(f"<ERR> SIGNAL_A011_4CMT: {e}, {msg}")
            traceback.print_exc()

    gesture_per_second: int = 10
    min_sample_time_ms: int = int(1.0 / gesture_per_second * 1000)#ms

    max_sample_analyze_time_s = 6#s
    max_sample_analyze_time_ms = 1000 * max_sample_analyze_time_s #ms
    max_sample_amount = max_sample_analyze_time_s * gesture_per_second

    def label_predict(self):
        try:
            ts, data = 0, None
            label_R, label_L = "None", "None"

            if len(self.data_to_gesture_prediction) >= 1:
                ## analiza względem ostatniej klasy
                buff: List = self.data_to_gesture_prediction.copy()

                ## kasowanie zbioru
                self.data_to_gesture_prediction.clear()
                buff.reverse()

                ## odnalezienie w próbie etykiety z rzeczywistymi wartościami landmark
                for ts, data in buff:
                    if not(data["Right"] is None or data["Left"] is None):
                        ts, data = buff.pop(-1)
                        break

                ## zamiana landmark na wektor wejściowy modelu tf
                if not(data["Right"] is None or data["Left"] is None):
                    # odczyt landmarków
                    gtrR, gtrL = landmark2array(data["Right"]), landmark2array(data["Left"])

                    ## normalizacja
                    NgtrR = normalization(gtrR,"Right", 0, **FALG_NORMALIZATION)
                    NgtrL = normalization(gtrL,"Left", 0, **FALG_NORMALIZATION)

                    ## predykcja bez wyświetlana czasu detekcji
                    predR = self.model.predict( NgtrR.reshape(1, 63), verbose=0 )
                    predL = self.model.predict( NgtrL.reshape(1, 63), verbose=0 )

                    ## dprzypisanie etykiety klasy
                    class_id_R = int(np.argmax(predR, axis=1)) ## array([1])
                    label_R = self.encoder.inverse_transform([class_id_R])[0]  ## array(['Gesture_A'])

                    class_id_L = int(np.argmax(predL, axis=1))  ## array([1])
                    label_L = self.encoder.inverse_transform([class_id_L])[0] ## array(['Gesture_A'])

            self.gestures.put( (ts, label_R, label_L) )

        except Exception as e:
            LOG.print(f"<ERR:UIC> Problem in CentralUnitThread.label_predict: {e}")

    def swap_label_detection(self):
        """
            Funkcja dodaje nowe słowa do listy aktywnych słów, bądź przedłuża czas trwania aktywnego gestu

        """
        try:
            buff = self.gestures.slice(0,9,1)
            mint = CentralUnitThread.min_sample_time_ms

            rarr: List[str] = [ b[1]  for b in buff]
            larr: List[str] = [ b[2]  for b in buff]

            def jump_condition(tab: List[str], active_lb) -> Tuple[bool, str | None]:
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
                lb_encoder = { ut: i+1 for i, ut in enumerate(set(tab)) }
                lb_encoder.update( {"None": 0} )

                lb_decoder = { v: k for k, v in lb_encoder.items()  }

                ## utworzenie wektora wejściowego
                Q_0 = [ lb_encoder[t] for t in tab]

                ## inicjacja modelu
                CA = CellularAutomaton(Q_0)

                ## uruchomienie modelu
                Q_stable = CA.run()

                ## odczytwanie wartości wektora wyjsciowego
                tab_process =  [ lb_decoder[q] for q in Q_stable]

                ## porównanie etykiety środkowej, wywołanie przeskoku
                if tab_process[4] != active_lb:
                    return True, tab_process[4]
                else:
                    return False, None

            for task, tab in [(self.task_right, rarr), (self.task_left, larr)]:

                cond, lb = jump_condition(tab, task.active_word)

                task.FLAG_jump_active = cond

                if cond:
                    task.new(lb, mint)
                else:
                    task.update(mint)
            pass
        except Exception as e:
            LOG.print(f"<ERR> Swap label detection proble: {e}")
            LOG.print(traceback.format_exc())

    def __init__(self):
        super().__init__()
        LOG.print(f"UIC: [INIT] Initialize thread")
        ## flagi
        self.FLAG_detection_active: bool = True

        ## model stworzony w celu detekcji gestów
        self.model = MODEL_H5.load(MODEL_H5.base_name)

        ## endkoder etykiet klas
        self.encoder = LabelEncoder()
        self.encoder.classes_ = NPY.load(NPY.classes, allow_pickle=True)

        ## zegar do póbkowania etykiet
        self.timer_detecte_sample = QTimer()
        self.timer_detecte_sample.timeout.connect( self.detection_active ) ## uruchomienie detekcji
        self.timer_detecte_sample.start(CentralUnitThread.min_sample_time_ms) ## interwał co 200ms

        ##
        self.data_to_gesture_prediction: List[Tuple[int, T_LeftRight]] = []

        ## tworzenie zbiornika wpyłenionego pustymi próbkami, zapisującego wykryte gesty w danym odstępie czasu
        self.gestures: CircularBuffer = CircularBuffer(CentralUnitThread.max_sample_amount)
        ## czas miedzy próbkami, etykieta prawa, etykieta lewa
        for _ in range(CentralUnitThread.max_sample_amount):
            self.gestures.put(  (0, "None", "None") )

        ## ustawienie struktury zestawu słów/Task dla lewj i prawej strony
        self.task_right = Task(Task.max_data_gesture, CentralUnitThread.max_sample_analyze_time_ms)
        self.task_left = Task(Task.max_data_gesture, CentralUnitThread.max_sample_analyze_time_ms)

        ## utorzenie koleki WordCoder
        self.word_coder: WordCoder = WordCoder( task_main=self.task_left, task_command=self.task_right )

        """
            dane informacyjne o wybranym kontrolerze
        """
        self.configurate = None
        self.control = None
        self.data_unit = None

    def run(self):
        try:
            LOG.print(f"UIC: [PROC] Activate CentralUnitThread run loop")
            while True:

                ## detekcja gestu co 200ms
                if self.FLAG_detection_active:
                    try:
                        ## reset flagi timera
                        self.FLAG_detection_active = False
                        # detekcja ostatniego gestu
                        self.label_predict()

                        ## wykrywanie przeskoku
                        self.swap_label_detection()

                        ## odświerzenie WordCodera
                        self.word_coder.check_for_new_status()

                        ## wysłanie aktualnego stanu kolejki do GUI
                        send_list_rr = [t[1] for t in self.gestures.get_buffer()]
                        send_list_ll = [t[2] for t in self.gestures.get_buffer()]
                        self.SIGNAL_A004_2GUI.emit(send_list_rr, send_list_ll)

                        ## przesył wykrytych etykiet oddzielnie dla każdej ręki
                        send_list_rr = self.task_right.get_label()
                        send_list_ll = self.task_left.get_label()
                        self.SIGNAL_A005_2GUI.emit(send_list_rr, send_list_ll)

                        ## przesył czasów etykiet
                        send_list_rr = self.task_right.get_value()
                        send_list_ll = self.task_left.get_value()
                        self.SIGNAL_A006_2GUI.emit(send_list_rr, send_list_ll)

                        ## przesył wartości kolejki kodera zapytań
                        send_list_queue = self.word_coder.get()
                        self.SIGNAL_A007_2GUI.emit(send_list_queue)

                        ## przesył tagów zapytań do GUI
                        if self.word_coder.FLAG_emit_SIGNAL_A008:
                            self.SIGNAL_A008_2GUI.emit( self.word_coder.DATA_emit_SIGNAL_A008 )

                        ## aktywacja protokołu połączenia z kontrolerami
                        if self.word_coder.FLAG_emit_SIGNAL_A009:
                            self.SIGNAL_A009_2CMT.emit( self.word_coder.DATA_emit_SIGNAL_A009  )

                        if self.word_coder.FLAG_emit_SIGNAL_A011:
                            self.SIGNAL_A011_2CMT.emit( self.word_coder.DATA_emit_SIGNAL_A011 )

                        self.word_coder.refresh_singal_2_basic_statu()

                    except Exception as e:
                        LOG.print(f"<ERR> CentralUnitThread, timer rate error: {e}")
                        LOG.print(traceback.format_exc())

                time.sleep(0.05)

        except Exception as e:
            LOG.print(f"<ERR> Problem in CentralUnitThread.run: {e}")
            LOG.print(traceback.format_exc())


    def detection_active(self):
        self.FLAG_detection_active = True

