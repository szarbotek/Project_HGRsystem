import traceback

from data.project_values import SERVER_IP, SERVER_PORT
from src.application.utils.ComunicationProtocol import *
from src.application.utils.structure import CircularBuffer

from data.project_values import LOG
from PyQt5.QtCore import QThread,  pyqtSignal, pyqtSlot
import socket
import time

import threading

class CommunicationThread(QThread):

    SIGNAL_A010_2UIC = pyqtSignal( object ) ## sygnał do przesyłąnia słownika końcowego

    """
        lista dostępnych kontrolerów
    """

    @pyqtSlot(bool)
    def SINGAL_A009_4UIC(self, activateConnection: bool):
        """
            Aktywacja/ zerwanie połączenia z robot serwer

        """
        print( "CommunicationThread", self.FLAG_activate_connection, activateConnection)
        self.FLAG_activate_connection = activateConnection

    @pyqtSlot(str)
    def SIGNAL_A011_4UIC(self, new_item: T_TagCommand ):
        """
            Dodanie nowej komendy do kolejki
        :param new_item:
        :return:
        """
        self.dataQueue.put( new_item )

    def __init__(self):
        super().__init__()
        LOG.print(f"CMT: [INIT] initialize thread ")

        ## net config z jsona ## <====
        self.ip = SERVER_IP
        self.port = SERVER_PORT

        self.FLAG_activate_connection: bool = False

        self.dataQueue: CircularBuffer = CircularBuffer(5) ## zbiornik na instukcje

        self.robotServer = None
        LOG.print(f"CMT: .[INFO] configurate base objects ")

    def run(self):
        ## petla wznawiajaca polaczenie z serwerem robota
        TAG = CommunicationTags.TAG

        while True:
            ## oczekiwanie na flage aktywacji połączenia
            if self.FLAG_activate_connection == False:
                time.sleep(5)
                LOG.print(f"CMT: .[INFO] waiting... ")
                continue
            else:
                LOG.print(f"CMT: .[INFO] Initialize connection to server ")

            try:
                self.robotServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                ## oczekiwanie na polaczenie z serwerem
                while True:
                    try:
                        ## connect
                        self.robotServer.connect((self.ip, self.port))
                        LOG.print(f"CMT: .[INFO] Connected successfully! {self.ip}:{self.port}")
                        ## przerwanie petli nawiazywania polaczenia z serwerem
                        break
                    except (socket.error, ConnectionRefusedError):
                        LOG.print(f"CMT: .[INFO] No available robot server. Wait 2 second to reno try")
                        time.sleep(5)


                ## zestaw instrukcji konfigurujących polaczenie z serwerem
                ## oczekiwanie na LOAD od servera
                initiatorLOAD = self.read()
                ## wysłąnie komunikatu o gotowości
                self.write(
                    CommunicationTags.WriteComandTags(TAG.READY)
                )

                ## informacja o aktywnych kontrolerach znalezionych przez serwer
                TagMsgDict = self.read()
                LOG.print(f"CMT: .[INFO] Find controllers {TagMsgDict}")

                tag, msg = CommunicationTags.ReadComandTags(TagMsgDict)
                self.SIGNAL_A010_2UIC.emit( (tag, msg) )

                while True:
                    ## oczekiwanie na Tag Command do aktywacji wyboru kontrolera
                    while len(self.dataQueue) == 0:
                        time.sleep(2)
                        continue

                    ##<<== wybur opcji z gestów, może emisja całego SELECT_OPTION
                    self.write( self.dataQueue.throw()  )

                    TagMsgDict = self.read()
                    tag, msg = CommunicationTags.ReadComandTags( TagMsgDict )

                    self.SIGNAL_A010_2UIC.emit( (tag, msg) )

                    if tag == TAG.ACCEPT:
                        LOG.print( f"CMT: .[INFO] Accept ")
                        break
                    else: LOG.print(msg)

                ## status kontrolera
                TagMsgDict = self.read()
                LOG.print( f"CMT: .[INFO] Controlers {TagMsgDict}" )
                tag, msg = CommunicationTags.ReadComandTags(TagMsgDict)
                self.SIGNAL_A010_2UIC.emit( (tag, msg) )

                ## sprawdzenie czy wszystkie parametry pozwalaja na kotrole robotem
                ## jesli tak rozpoczecie pretli wysylania rokzow

                while True:
                    ## rozłaczenie z serwerem
                    if self.FLAG_activate_connection == False: break

                    if len(self.dataQueue) == 0:
                        nontag = CommunicationTags.WriteComandTags(TAG.NONE)
                        self.dataQueue.put( nontag )

                    if len(self.dataQueue) > 0:

                        # self.robotServer.settimeout(1.0)
                        # try:
                        ## pobranie elementu do kolejki na wypadek jej skasowania

                        tagDictMsg = self.read()
                        buff = self.dataQueue.throw()

                        tag, msg = CommunicationTags.ReadComandTags(tagDictMsg)
                        ## oczekiwanie na tag LOAD
                        if tag == TAG.LOAD:
                            ## próba wysłania złego Tag command
                            if buff == "" or buff == None or buff == []:
                                buff = CommunicationTags.WriteComandTags("None")

                            ## przeslanie do serwera robota instrukcji do wykonania
                            LOG.print(f"CMT: .[INFO] {buff} ")
                            self.write( buff )

                            ## oczekiwanie na komunikat zwrotny od serwera
                            TagMsgDict = self.read()
                            tag, msg = CommunicationTags.ReadComandTags(TagMsgDict)
                            self.SIGNAL_A010_2UIC.emit((tag, msg))

                        elif tag == TAG.CLOSE:
                            break
                        else:
                            LOG.print( f"<ERR> wrong data tag emit {tag}")
                            break

                        # except socket.timeout:
                        #     LOG.print()("[INFO] Waiting for LOAD#")


                    time.sleep(2.100)#ms

            except Exception as e:
                LOG.print("<ERR> Lost connection to server", e)
                traceback.print_exc()
            LOG.print("<ERR> Repeat process connection")
            ## zmkniecie obecnej instancji servera
            self.robotServer.close()
            ## usuniecie starej konfiguracji
            del self.robotServer


    def read(self)->str:
        # time.sleep(0.015) ## 20ms na przygotowania sie do doczytu
        buffor = self.robotServer.recv(1024)  # LOAD
        msg = buffor.decode('utf-8')
        LOG.print( f"Recive: >>{msg}<<" )
        return msg

    def write(self, msg):
        buffor = msg.encode('utf-8')
        self.robotServer.sendall(buffor)
        LOG.print( f"Emit: <<{msg}>>")