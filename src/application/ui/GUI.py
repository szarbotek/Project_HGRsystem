import json

import mediapipe as mp
from PyQt5.QtGui import QColor

from data.project_values import *
from application.core.CAM import CameraThread
from application.core.UIC import CentralUnitThread
from application.core.MPR import MediapipeRecognizer
from application.core.CMT import CommunicationThread

from application.utils.HandGastureControlSystem import WordCoder, Task
from application.utils.ComunicationProtocol import CommunicationTags

from application.ui.components.jp_camera_screen import JpCameraScreen
from application.ui.components.jp_widget import JpWidget
from application.ui.components.jp_push_button import JpPushButton

from application.ui.components.flow_chart import FlowChart
from application.ui.components.word_queue import WordQueue
from application.ui.components.jumping_machine import JumpingMachine
from application.ui.components.icon_image import StaticIconImage, DoubleIconImage,MultiIconImage
from application.ui.components.display_data import DisplayData
from application.ui.components.logs_box import LogsBox

from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QGridLayout,QLabel, QVBoxLayout, QPushButton, QPlainTextEdit, QSpacerItem, QSizePolicy
from PyQt5.QtCore import Qt, QTimer, QMetaObject, Q_ARG, pyqtSlot


from typing import Tuple, List, Dict


class MainWindow(QMainWindow):

    def SIGNAL_A000_4CAM(self, *args):
        try:
            ## sprawdzenie struktury przesyłu danych
            assert len(args) == 2, IndexError
            ## zapsianie danych klatki do Wigetu odpowiedzialnego za wyswietlanie
            ts = args[0]
            frame = args[1]
            self.ImageScraane.new_frame( ts, frame )
        except Exception as e:
            LOG.print(f"<ERR:{self.__class__}> SIGNAL_A000_4CAM: {e}, {args}")

    def SIGNAL_A002_4MPR(self, *args):
        try:
            ## sprawdzenie struktury przesyłu danych
            assert len(args) == 2, IndexError
            ## zapsianie danych landmarków do Wigetu odpowiedzialnego za wyswietlanie
            ts = args[0]
            landmarks = args[1]
            self.ImageScraane.new_landmarks( ts, landmarks )
        except Exception as e:
            LOG.print(f"<ERR:{self.__class__}> SIGNAL_A002_4MPR: {e}, {args}")

    def SIGNAL_A004_4UIC(self, *args):
        try:
            ## sprawdzenie kolejki struktury przesyłu danych
            assert len(args) == 2, IndexError
            rr = args[0]
            ll = args[1]
            ## zapsianie danych do Wigetu odpowiedzialnego za wyswietlanie
            self.fc_right.new_data(rr)
            self.fc_left.new_data(ll)
        except Exception as e:
            LOG.print(f"<ERR:{self.__class__}>  SIGNAL_A004_4UIC: {e}, {args}")

    def SIGNAL_A005_4UIC(self, *args):
        try:
            ## sprawdzenie kolejki struktury przesyłu danych
            assert len(args) == 2, IndexError
            rr = args[0]
            ll = args[1]
            ## zapsianie danych do Wigetu odpowiedzialnego za wyswietlanie
            self.wq_right_task_label.new_data(rr)
            self.wq_left_task_label.new_data(ll)
        except Exception as e:
            LOG.print(f"<ERR:{self.__class__}> SIGNAL_A003_4UIC: {e}, {args}")

    def SIGNAL_A006_4UIC(self, *args):
        try:
            ## sprawdzenie kolejki struktury przesyłu danych
            assert len(args) == 2, IndexError
            rr = args[0]
            ll = args[1]
            ## zapsianie danych do Wigetu odpowiedzialnego za wyswietlanie
            self.wq_right_task_time.new_data(rr, text_f=r"{} ms")
            self.wq_left_task_time.new_data(ll, text_f=r"{} ms")
        except Exception as e:
            LOG.print(f"<ERR:{self.__class__}>  SIGNAL_A006_4UIC: {e}, {args}")

    def SIGNAL_A007_4UIC(self, *args):
        try:
            ## sprawdzenie kolejki struktury przesyłu danych
            assert len(args) == 1, IndexError
            queue = args[0]
            ## zapsianie danych do Wigetu odpowiedzialnego za wyswietlanie
            self.word_coder_disp.new_data(queue)

            if WordCoder.QUESTION.MOV in queue:
                self.help_box_hints.index = 0
            elif WordCoder.QUESTION.INTERACT in queue:
                self.help_box_hints.index = 1
            elif WordCoder.QUESTION.CONNECT in queue:
                self.help_box_hints.index = 2
            elif WordCoder.QUESTION.RUNSYS in queue:
                self.help_box_hints.index = 3
            elif WordCoder.QUESTION.MOVSYS in queue:
                self.help_box_hints.index = 4
            else:
                self.help_box_hints.index = 5
            self.help_box_hints.update()

        except Exception as e:
            LOG.print(f"<ERR:{self.__class__}> SIGNAL_A007_4UIC: {e}, {args}, {len(args)}")

    def SIGNAL_A008_4UIC(self, *args):
        try:
            ## sprawdzenie kolejki struktury przesyłu danych
            assert len(args) == 1, IndexError
            tag = args[0]
            ## wywołanie eventu w kolejce GUI
            QMetaObject.invokeMethod(
                self,
                "tagEvent",
                Qt.QueuedConnection,
                Q_ARG(object, tag)
            )
        except Exception as e:
            LOG.print(f"<ERR> SIGNAL_A008_4UIC: {e}, {args}")

    def SIGNAL_A012_4UIC(self, *args):
        try:
            ## sprawdzenie kolejki struktury przesyłu danych
            assert len(args) == 1, IndexError
            info = args[0]

            tag, msg = info

            if tag == CommunicationTags.TAG.MESSAGE:
                data_unit: Dict = msg.get(CommunicationTags.MessageDictKeys.dataUnit)

                string_pos = data_unit.pop(CommunicationTags.MessageDictKeys.Pos)

                pos_val = json.loads( string_pos )
                pos_key = ["x", "y", "z"]
                self.positons_data_display.set_data( dict(zip(pos_key, pos_val))  )

                self.robot_information.set_data( data_unit )

                retmsg: str = msg.get(CommunicationTags.MessageDictKeys.msg)
                if "RUN" in retmsg:
                    self.ico_run_status.FALG_state = True
                    self.ico_stop_status.FALG_state = False

                    module_name = retmsg.split('>')[1].split('<')[0]
                    if module_name == "": module_name = "None"
                    self.label_active_program_selected.setText( module_name )

                    self.ico_run_status.update()
                    self.ico_stop_status.update()
                    self.label_active_program_selected.update()
                elif "STOP" in retmsg:
                    self.ico_run_status.FALG_state = False
                    self.ico_stop_status.FALG_state = True
                    self.ico_run_status.update()
                    self.ico_stop_status.update()
                    self.label_active_program_selected.update()
                elif "RESUME" in retmsg:
                    self.ico_run_status.FALG_state =  True
                    self.ico_stop_status.FALG_state = False
                    self.ico_run_status.update()
                    self.ico_stop_status.update()
                    self.label_active_program_selected.update()

            elif tag == CommunicationTags.TAG.CONTROL:
                pgrs: Dict = msg.get(CommunicationTags.MessageDictKeys.programs )
                self.programs_queue.data = list( pgrs.keys() )

                vals: Dict = msg.get(CommunicationTags.MessageDictKeys.values )
                if vals.get( CommunicationTags.MessageDictKeys.OperatingMode ) == "Auto":
                    self.ico_AUTO_status.FALG_state = True
                    self.ico_AUTO_status.update()
                if vals.get( CommunicationTags.MessageDictKeys.Access ) == "Aprove":
                    self.ico_lock_status.FALG_state = True
                    self.ico_lock_status.update()
                if vals.get( CommunicationTags.MessageDictKeys.State ) == "MotorsOn":
                    self.ico_motor_status.FALG_state = True
                    self.ico_motor_status.update()
                pass

            elif tag == CommunicationTags.TAG.CONFIGURATE:
                self.net_status.FALG_state = True
                self.net_status.update()
                dc: Dict = msg.get( CommunicationTags.MessageDictKeys.controllers )

                self.controller_queue.data = list( dc.keys() )
                self.controller_data_display.set_data(dc.get('0'))

                self.ico_AUTO_status.FALG_state = False
                self.ico_AUTO_status.update()
                self.ico_lock_status.FALG_state = False
                self.ico_lock_status.update()
                self.ico_motor_status.FALG_state = False
                self.ico_motor_status.update()

                pass

        except Exception as e:
            LOG.print(f"<ERR> SINGAL_A012_4UIC: {e}, {args}")

    ### ================================================================================================================

    refresh_time_ms = 12  # ms

    def __init__(self):
        super().__init__()
        LOG.print(f"GUI: [INIT] initialize thread ")

        self.setFixedSize(1520, 800)
        self.setStyleSheet("background-color: #000000;")

        ## timer odświerzania grafik w GUI, screen, queue
        self.timerRefresh = QTimer()
        self.timerRefresh.timeout.connect( self.refresh )
        self.timerRefresh.start( MainWindow.refresh_time_ms) ## odświerzanie paintEvent

        self.build()
        self.start_thread()
        self.show()

    def build(self):
        try:
            LOG.print(f"GUI: [PROC] -- start build -- ")

            section_camera_screen = None
            section_help_box  = None
            section_detection_signal  = None
            section_logs = None
            section_question_queue  = None
            section_robot_server = None

            ## ustawienie szerokosci ramki
            JpWidget.thickness = 4
            JpWidget.thickness = 4

            ### inicjacja głównego okna aplikacji
            win = JpWidget(self)
            win.setFixedSize( self.width(), self.height() )
            win.color_background = QColor(24, 46, 97)
            grid_main_win = QGridLayout(win)

            ### === inicjacja sekcji kamery ============================================================================
            try:
                section_camera_screen: JpWidget = JpWidget(win)
                # section_camera_screen.setFixedSize
                section_camera_screen.color_background = QColor(238, 209, 49)## yellow

                grid_section_CS = QGridLayout(section_camera_screen)

                # button_CS_swap_main_hand = JpPushButton(section_camera_screen)
                # button_CS_swap_main_hand.setFixedSize(80,40)

                button_CS_swap_main_hand = JpWidget(section_camera_screen)
                button_CS_swap_main_hand.setFixedSize(80, 40)
                button_CS_swap_main_hand.color_background = QColor(34, 198, 78)
                ltico1 = QGridLayout(button_CS_swap_main_hand)
                ltico1.setContentsMargins(0, 0, 0, 0)
                ltico1.addWidget(
                    StaticIconImage(button_CS_swap_main_hand, path=PATH.assets_ui + "show_landmark.png", size=30)
                )

                button_CS_camL = JpWidget(section_camera_screen)
                button_CS_camL.setFixedSize(80, 40)
                button_CS_camL.color_background = QColor(34, 198, 78)
                ltico2 = QGridLayout(button_CS_camL)
                ltico2.setContentsMargins(0, 0, 0, 0)
                ltico2.addWidget(
                    StaticIconImage(button_CS_camL, path=PATH.assets_ui + "swap_main_hand.png", size=30)
                )
                button_CS_camR = JpWidget(section_camera_screen)
                button_CS_camR.setFixedSize(80, 40)
                button_CS_camR.color_background = QColor(34, 198, 78)
                ltico3 = QGridLayout(button_CS_camR)
                ltico3.setContentsMargins(0, 0, 0, 0)
                ltico3.addWidget(
                    StaticIconImage(button_CS_camR, path=PATH.assets_ui + "hide_screen.png", size=30)
                )
                button_CS_show_landmark = JpWidget(section_camera_screen)
                button_CS_show_landmark.setFixedSize(80, 40)
                button_CS_show_landmark.color_background = QColor(34, 198, 78)
                ltico4 = QGridLayout(button_CS_show_landmark)
                ltico4.setContentsMargins(0, 0, 0, 0)
                ltico4.addWidget(
                    StaticIconImage(button_CS_show_landmark, path=PATH.assets_ui + "hide_camera.png", size=40)
                )

                self.ImageScraane = JpCameraScreen(section_camera_screen)
                self.ImageScraane.setFixedSize(576, 324)

                grid_section_CS.addWidget( button_CS_swap_main_hand, 0, 0)
                grid_section_CS.addWidget( button_CS_camL, 0, 1)
                grid_section_CS.addWidget( button_CS_camR, 0, 2)
                grid_section_CS.addWidget( button_CS_show_landmark, 0, 3)
                grid_section_CS.addWidget(self.ImageScraane, 1, 0, 1, 5)
            except: pass
            ### === inicjacja help-box / poradnik ======================================================================
            try:
                section_help_box: JpWidget = JpWidget(win)
                # section_help_box.setGeometry( section_camera_screen.width(), 0, section_question_queue.width()+section_detection_signal.width()-section_camera_screen.width()+padding  , section_camera_screen.height()+padding )
                section_help_box.color_background = QColor(246, 252, 252)## withe
                lwhb1 = QGridLayout(section_help_box)
                # print([ os.path.join( PATH.assets_ui_helpbox, hb)
                #                                 for hb in os.listdir(PATH.assets_ui_helpbox)], "=========================================================================")

                self.help_box_hints = MultiIconImage(section_help_box,
                                            paths=[
                                                'P:\\INZ\\ProjectPD\\assets/ui/helpbox/move.png',
                                                'P:\\INZ\\ProjectPD\\assets/ui/helpbox/interact.png',
                                                'P:\\INZ\\ProjectPD\\assets/ui/helpbox/connect.png',
                                                'P:\\INZ\\ProjectPD\\assets/ui/helpbox/runsys.png',
                                                'P:\\INZ\\ProjectPD\\assets/ui/helpbox/movsys.png',
                                                'P:\\INZ\\ProjectPD\\assets/ui/helpbox/base.png',
                                            ],
                                            index=5, size=400)
                lwhb1.addWidget(self.help_box_hints, 0, 0)

                grid_section_HB = QGridLayout( section_help_box )
            except Exception as e: print(e, "<<<<<<")
            ### === inicjacja sekcji wykrywania i informacji o próbkowaniu==============================================
            try:
                section_detection_signal: JpWidget = JpWidget(win)
                # section_detection_signal.setGeometry( 0, section_camera_screen.height(), 840, 200 )
                section_detection_signal.color_background = QColor(45, 84, 179)## light blue

                grid_section_DS = QGridLayout( section_detection_signal )

                self.fc_right = FlowChart(section_detection_signal, 60)
                self.fc_right.setFixedSize(320,60)
                self.fc_left = FlowChart(section_detection_signal, 60)
                self.fc_left.setFixedSize(320,60)

                icon_main_hand: StaticIconImage = StaticIconImage(section_detection_signal, path=PATH.assets_ui_hand_L, size=60)
                icon_control_hand: StaticIconImage = StaticIconImage(section_detection_signal, path=PATH.assets_ui_hand_R, size=60)

                self.wq_right_task_label = WordQueue(section_detection_signal, Task.max_data_gesture)
                self.wq_right_task_label.color_background = QColor(147, 166, 217)
                self.wq_right_task_label.font_size = 8

                self.wq_right_task_time = WordQueue(section_detection_signal, Task.max_data_gesture)
                self.wq_right_task_time.color_background = QColor(147, 166, 217)

                self.wq_left_task_label = WordQueue(section_detection_signal, Task.max_data_gesture)
                self.wq_left_task_label.color_background = QColor(147, 166, 217)
                self.wq_left_task_label.font_size = 8

                self.wq_left_task_time = WordQueue(section_detection_signal, Task.max_data_gesture)
                self.wq_left_task_time.color_background = QColor(147, 166, 217)

                grid_section_DS.addWidget( self.fc_left, 0, 0, 2, 1 )
                grid_section_DS.addWidget( self.fc_right, 2, 0, 2, 1 )
                grid_section_DS.addWidget( icon_main_hand, 0, 1, 2, 1 )
                grid_section_DS.addWidget( icon_control_hand, 2, 1, 2, 1 )

                grid_section_DS.addWidget( self.wq_left_task_label, 0, 2)
                grid_section_DS.addWidget( self.wq_left_task_time, 1, 2)
                grid_section_DS.addWidget(self.wq_right_task_label, 2, 2)
                grid_section_DS.addWidget(self.wq_right_task_time, 3, 2)
            except: pass
            ### === inicjacja sekcji logów =============================================================================
            try:
                section_logs: JpWidget = JpWidget(win)
                # section_detection_signal.setGeometry( 0, section_camera_screen.height(), 840, 200 )
                section_logs.color_background = QColor(246, 252, 252)## withe

                grid_section_LG = QGridLayout( section_logs )

                self.log_object = LogsBox(section_logs)
                # self.log_object.setReadOnly(True)
                # self.log_object.setStyleSheet("""
                #     QPlainTextEdit {
                #         background-color: white;
                #         color: black;
                #         font-family: Consolas;
                #         font-size: 10pt;
                #     }
                # """)

                grid_section_LG.addWidget( self.log_object, 0, 0)
            except: pass
            ### === inicjacja wyświetlania kolejki odpytań =============================================================
            try:
                section_question_queue: JpWidget = JpWidget(win)
                section_question_queue.setFixedWidth(200)
                section_question_queue.color_background = QColor(181, 65, 123)## light blue

                grid_section_QQ = QGridLayout( section_question_queue )

                self.word_coder_disp = WordQueue( section_question_queue, WordCoder.max_word_in_queue, "Down" )
                self.word_coder_disp.color_background = QColor(222, 102, 162)
                self.word_coder_disp.font_size = 14

                grid_section_QQ.addWidget( self.word_coder_disp, 0, 0)
            except: pass
            ### === inicjacja panelu komunikacji i zarządzania robotem =================================================
            try:
                section_robot_server: JpWidget = JpWidget(win)
                section_robot_server.setFixedWidth(480)
                section_robot_server.color_background = QColor(228, 112, 33)## orange

                grid_section_RS = QGridLayout( section_robot_server )

                ## =====================================================================================================
                self.net_status: DoubleIconImage = DoubleIconImage(section_robot_server,
                        pathAcc=os.path.join(PATH.assets_ui, "wifi_connect.png"),
                        pathDis=os.path.join(PATH.assets_ui, "wifi_disconnect.png"),
                        base_state=False,
                        size=40
                    )

                ip_port_info = QLabel( f"{SERVER_IP}: {SERVER_PORT}",  section_robot_server,)
                ip_port_info.setStyleSheet("""
                    QLabel {
                        background-color: #FFF3EB;
                        border: 1px solid #dcdcdc;
                        border-radius: 15px;
                        font-size: 16px;
                        font-family: "Segoe UI";
                        font-weight: bold;
                        color: black;
                        qproperty-alignment: 'AlignCenter';
                    }
                """)

                ## =====================================================================================================
                section_run_system = JpWidget(section_robot_server)
                section_run_system.setFixedHeight( 80 )
                section_run_system.color_background = QColor(172, 83, 30)## dark orange

                grip_section_run_system = QGridLayout( section_run_system )

                # Status Pracy (Run)
                self.ico_run_status: DoubleIconImage = DoubleIconImage(
                    section_run_system,
                    pathAcc=os.path.join(PATH.assets_ui, "run_on.png"),
                    pathDis=os.path.join(PATH.assets_ui, "run_off.png"),
                    base_state=False,
                    size=50
                    )

                # Status Zatrzymania (Stop)
                self.ico_stop_status: DoubleIconImage = DoubleIconImage(
                    section_run_system,
                    pathAcc=os.path.join(PATH.assets_ui, "stop_on.png"),
                    pathDis=os.path.join(PATH.assets_ui, "stop_off.png"),
                    base_state=False,
                    size=50
                    )

                # Status Wznowienia (Resume)
                self.label_active_program_selected: QLabel = QLabel("None", section_run_system)
                self.label_active_program_selected.setStyleSheet("""
                QLabel {
                        background-color: white;
                        border: 2px solid rgba(0, 0, 0, 200);
                        border-radius: 20px;
                        font-family: "Segoe UI";
                        font-size: 14px;
                        padding: 0px;
                    }
                """)
                self.label_active_program_selected.setAlignment(Qt.AlignCenter)


                grip_section_run_system.addWidget(self.ico_run_status, 0, 0)
                grip_section_run_system.addWidget(self.ico_stop_status, 0, 1)
                grip_section_run_system.addWidget(self.label_active_program_selected, 0, 2)


                ## =====================================================================================================
                section_robot_status = JpWidget(section_robot_server)
                section_robot_status.color_background = QColor(172, 83, 30)## dark orange

                grip_section_robot_status = QGridLayout( section_robot_status )

                ## status trybu pracy robota
                self.ico_AUTO_status: DoubleIconImage = DoubleIconImage(section_robot_status,
                        pathAcc=os.path.join(PATH.assets_ui, "auto.png"),
                        pathDis=os.path.join(PATH.assets_ui, "manual.png"),
                        base_state=False,
                        size=140
                        )

                ## status dostępu
                self.ico_lock_status: DoubleIconImage = DoubleIconImage(section_robot_status,
                        pathAcc=os.path.join(PATH.assets_ui, "access_on.png"),
                        pathDis=os.path.join(PATH.assets_ui, "access_off.png"),
                        base_state=False,
                        size=80
                    )

                ## Status Silnika (Motor)
                self.ico_motor_status: DoubleIconImage = DoubleIconImage(section_robot_status,
                        pathAcc=os.path.join(PATH.assets_ui, "motor_on.png"),
                        pathDis=os.path.join(PATH.assets_ui, "motor_off.png"),
                        base_state=False,
                        size=80
                    )

                grip_section_robot_status.addWidget(self.ico_AUTO_status, 0, 0, 1, 2, Qt.AlignCenter)
                grip_section_robot_status.addWidget(self.ico_lock_status, 1, 0, Qt.AlignCenter)
                grip_section_robot_status.addWidget(self.ico_motor_status, 1, 1, Qt.AlignCenter)

                ## =====================================================================================================
                section_positons = JpWidget(section_robot_server)
                # section_positons.setFixedHeight( 150 )
                section_positons.color_background = QColor(172, 83, 30)## dark orange

                grid_section_positons = QGridLayout(section_positons)

                self.positons_data_display = DisplayData(section_positons)
                # self.positons_data_display.color_background = QColor(172, 83, 30)
                self.positons_data_display.font_size = 8
                self.positons_data_display.ferdieling = 0.75

                grid_section_positons.addWidget( self.positons_data_display , 0, 0)

                ## =====================================================================================================
                section_controller_information = JpWidget(section_robot_server)
                section_controller_information.color_background = QColor(172, 83, 30)

                grid_section_controller_information = QGridLayout( section_controller_information  )

                self.controller_data_display = DisplayData(section_controller_information)
                self.controller_data_display.font_size = 8

                grid_section_controller_information.addWidget(self.controller_data_display, 0, 0)

                ## =====================================================================================================
                section_robot_information = JpWidget(section_robot_server)
                section_robot_information.setFixedWidth(340)
                section_robot_information.color_background = QColor(172, 83, 30)

                self.robot_information = DisplayData(section_robot_information)
                self.robot_information.font_size = 14

                grid_section_robot_information = QGridLayout( section_robot_information )

                grid_section_robot_information.addWidget( self.robot_information, 0,0 )

                ## =====================================================================================================
                self.controller_queue: WordQueue = WordQueue(section_robot_server, 5, "Left")
                self.controller_queue.setFixedHeight(50)
                self.controller_queue.color_background = QColor(52, 140, 46)

                ## =====================================================================================================
                self.programs_queue: WordQueue = WordQueue(section_robot_server, 8, "Up")
                self.programs_queue.setFixedHeight(300)
                self.programs_queue.font_size = 10
                self.programs_queue.color_background = QColor(52, 140, 46)


                ## =====================================================================================================

                grid_section_RS.addWidget( self.net_status, 0, 0, 1, 1 )
                grid_section_RS.addWidget( ip_port_info, 0, 1, 1, 2 )
                grid_section_RS.addWidget( section_robot_status, 0, 3, 3, 1 )

                grid_section_RS.addWidget( self.controller_queue, 1, 0, 1, 3 )

                grid_section_RS.addWidget( section_controller_information , 2, 0, 2, 3 )

                grid_section_RS.addWidget( section_positons, 3, 3, 2, 1)

                grid_section_RS.addWidget( section_run_system, 4, 0, 1, 3)
                grid_section_RS.addWidget( self.programs_queue, 5, 0, 1, 2 )
                grid_section_RS.addWidget( section_robot_information, 5, 2, 1, 2 )
            except: pass

            grid_main_win.addWidget( section_camera_screen, 0, 0)
            grid_main_win.addWidget( section_help_box, 0, 1, 1, 2)
            grid_main_win.addWidget( section_detection_signal, 1, 0, 1, 2)
            grid_main_win.addWidget( section_logs, 2,0, 1, 2)
            grid_main_win.addWidget( section_question_queue, 1,2, 2, 1)
            grid_main_win.addWidget( section_robot_server, 0, 3, 3, 1)

            self.show()

            JumpingMachine.generate_connetion()
            JumpingMachine.set_cursor( win )

            LOG.print(f"GUI: .[INFO] end build proc ")

        except Exception as e:
            LOG.print(f"<ERR> GUI build error: {e}")

    def start_thread(self):
        try:
            ### === tworzenie instancji wątku ==========================================================================
            self.GUI = self
            self.UIC = CentralUnitThread()
            self.CAM = CameraThread()
            self.MPR = MediapipeRecognizer()
            self.CMT = CommunicationThread()

            ### === ustawanie sygnałów obioru ==========================================================================
            self.CAM.SIGNAL_A000_2GUI.connect( self.GUI.SIGNAL_A000_4CAM)
            self.CAM.SIGNAL_A001_2MPR.connect( self.MPR.SIGNAL_A001_4CAM)
            self.MPR.SIGNAL_A002_2GUI.connect( self.GUI.SIGNAL_A002_4MPR)
            self.MPR.SIGNAL_A003_2UIC.connect( self.UIC.SIGNAL_A003_4MPR)
            self.UIC.SIGNAL_A004_2GUI.connect( self.GUI.SIGNAL_A004_4UIC)
            self.UIC.SIGNAL_A005_2GUI.connect( self.GUI.SIGNAL_A005_4UIC)
            self.UIC.SIGNAL_A006_2GUI.connect( self.GUI.SIGNAL_A006_4UIC)
            self.UIC.SIGNAL_A007_2GUI.connect( self.GUI.SIGNAL_A007_4UIC)
            self.UIC.SIGNAL_A008_2GUI.connect( self.GUI.SIGNAL_A008_4UIC)
            self.UIC.SIGNAL_A009_2CMT.connect( self.CMT.SINGAL_A009_4UIC)
            self.CMT.SIGNAL_A010_2UIC.connect( self.UIC.SIGNAL_A010_4CMT)
            self.UIC.SIGNAL_A011_2CMT.connect( self.CMT.SIGNAL_A011_4UIC)
            self.UIC.SIGNAL_A012_2GUI.connect( self.GUI.SIGNAL_A012_4UIC)

            ### === uruchamianie wątków ================================================================================
            self.CAM.start()
            self.MPR.start()
            self.UIC.start()
            self.CMT.start()

        except Exception as e:
            import traceback
            LOG.print(f"<ERR:MainWindow> Start thread, error: {e}")
            LOG.print( traceback.format_exc() )

    @pyqtSlot(object)
    def tagEvent(self, event:tuple[str]):

        ## przemapowanie komendy ruchu wysyłanej z kodera na odpowiednie tagi JumpingMachine
        tag_covert_2_gui_eperation: Dict[Tuple[str, ...], str] = {
            (WordCoder.QUESTION.MOV, WordCoder.OPTION.RIGHT): "D",
            (WordCoder.QUESTION.MOV, WordCoder.OPTION.LEFT): "A",
            (WordCoder.QUESTION.MOV, WordCoder.OPTION.UP): "W",
            (WordCoder.QUESTION.MOV, WordCoder.OPTION.DOWN): "S",
            (WordCoder.QUESTION.MOV, WordCoder.OPTION.IN): "IN",
            (WordCoder.QUESTION.MOV, WordCoder.OPTION.OUT): "OUT", ## dodać odwołanie do JPM
            (WordCoder.QUESTION.INTERACT, WordCoder.OPTION.PUSH_BUTTON, WordCoder.OPTION.ACTIVATE_OBJECT): "PRESSED",
            (WordCoder.QUESTION.INTERACT, WordCoder.OPTION.PUSH_BUTTON, WordCoder.OPTION.DEACTIVATE_OBJECT): "RELEASED",
        }

        try:
            if event in tag_covert_2_gui_eperation:
                if event[0] == WordCoder.QUESTION.MOV:
                    ## wykonanie instrukcji skoku
                    JumpingMachine.movement_courser.jump(
                        tag_covert_2_gui_eperation[event]
                    )
                if event[0] == WordCoder.QUESTION.INTERACT:
                    ## akcja dla przycisku typu push
                    if event[1] == WordCoder.OPTION.PUSH_BUTTON:
                        ## sprawdzenie czy obiekt aktywny na kursorze jest faktycznie przyciskiem
                        if isinstance(JumpingMachine.movement_courser, JpPushButton):
                            ## wciśniecie przycisku
                            if tag_covert_2_gui_eperation[event] == "PRESSED":
                                JumpingMachine.movement_courser.pressed.emit()
                            elif tag_covert_2_gui_eperation[event] == "RELEASED":
                                JumpingMachine.movement_courser.released.emit()
                            pass
        except Exception as e:
            LOG.print(f"<ERR> tagEvent: {e}")

    def keyPressEvent(self, event):
        try:
            # wysyłanie sygnałów ruchu do kursora
            if JumpingMachine.FLAG_is_connection_generate:
                if event.key() == Qt.Key_W:
                    JumpingMachine.movement_courser.jump('W')
                elif event.key() == Qt.Key_S:
                    JumpingMachine.movement_courser.jump('S')
                elif event.key() == Qt.Key_A:
                    JumpingMachine.movement_courser.jump('A')
                elif event.key() == Qt.Key_D:
                    JumpingMachine.movement_courser.jump('D')
                elif event.key() == Qt.Key_Q:
                    JumpingMachine.movement_courser.jump('OUT')
                elif event.key() == Qt.Key_E:
                    JumpingMachine.movement_courser.jump('IN')
            else:
                print("Not generate connections")
        except Exception as e:
            print(e)

    def refresh(self):
        """
            Event do odświerzania Wigetów dynamicznych
        """

        try:
            self.log_object.refresh( LOG.datamsg )

            ## odświerzanie obrazu z kamery
            self.ImageScraane.refresh( self.refresh_time_ms )

            ## odświerzenie FlowChart
            self.fc_right.refresh( self.refresh_time_ms )
            self.fc_left.refresh( self.refresh_time_ms )

            ## odświerzenie WordQueue
            self.wq_right_task_label.update()
            self.wq_left_task_label.update()
            self.wq_right_task_time.update()
            self.wq_left_task_time.update()

            self.programs_queue.update( )
            self.controller_queue.update( )

            ## odświerzenie kolejki kodera
            self.word_coder_disp.update()

            ## oświerzenie informacji

            pass

        except Exception as e:
            LOG.print(f"<ERR> Refresh error: {e}")



def activate():
    """
        Aktywacja instancji GUI
    """
    app = QApplication(sys.argv)

    win = MainWindow()
    win.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    activate()