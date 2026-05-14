from data.project_values import LOG

from enum import Enum

from typing import List, Dict, Tuple, Any, NewType

T_TagCommand =  NewType("T_TagCommand", str)
T_DictionaryMessage =  NewType("T_DictionaryMessage", Dict[str, str | Dict[str, Any]])

class CommunicationTags:

    NONTAG: T_TagCommand = "NONE#"

    class TAG(str, Enum):
        HASH = "#"
        LOAD = "LOAD"
        READY = "READY"
        SELECT_OPTION = "SELECT_OPTION"
        ACCEPT = "ACCEPT"
        WRONG = "WRONG"
        CLOSE = "CLOSE"
        NONE = "NONE"
        RUNSYS = "RUNSYS"
        MOVSYS = "MOVSYS"
        CONFIGURATE = "CONFIGURATE"
        CONTROL = "CONTROL"
        MESSAGE = "MESSAGE"

    class CMD(str, Enum):
        SEPARATOR = "*"
        ## RUNSYS
        RUN = "RUN"
        STOP = "STOP"
        RESUME = "RESUME"
        ## MOVSYS

    class MessageDictKeys(str, Enum):
        controllers = "controllers"
        programs = "programs"
        values = "values"
        dataUnit = "dataUnit"
        Pos = "Pos"
        OperatingMode = "OperatingMode"
        Access = "Access"
        State = "State"
        msg = "msg"

    @staticmethod
    def conver_MsgDict_2_Dict(msgDict) -> Dict[str, str | Dict]:
        """
            Funkcja zamienia słownik zapisany w stringu na słownik pythonowy wypełniony stringami
        :param msgDict:
        :return:  Słownik Pythona
        """

        ##
        def removeAddComma(msgDict: str):
            ## usuniecie nadmiarowych przecinkow
            buff: str = msgDict[::-1]

            FLAG_REPLACE = False
            for i, b in enumerate(buff):
                if b == " ":
                    continue
                elif b == "}":
                    FLAG_REPLACE = True
                elif b == "," and FLAG_REPLACE:
                    buff = buff[:i] + " " + buff[i + 1:]
                else:
                    FLAG_REPLACE = False
                    continue

            return buff[::-1]

        ##
        def transformToDict(msgDict: str) -> Dict[str, str | Dict]:
            inBracekt = msgDict[1:-1]
            ret: Dict[str, str | Dict] = {}

            keys = []
            vals = []

            buff = ""
            FALG_OPEN_BRACKET = 0
            for sing in inBracekt:
                ## pakowanie elementow w nawiasie
                if sing == "{" or sing == "(" or sing == "[":
                    FALG_OPEN_BRACKET += 1
                if sing == "}" or sing == ")" or sing == "]":
                    FALG_OPEN_BRACKET -= 1

                if FALG_OPEN_BRACKET == 0:
                    if sing in ":":
                        ## dodanie klucza
                        keys.append(buff)
                        buff = ""
                    elif sing in ",":
                        vals.append(buff)
                        buff = ""
                    else:
                        buff += sing
                else:
                    buff += sing
            else:
                vals.append(buff)
                buff = ""

            ret = {
                k: (transformToDict(v) if (set("{}") <= set(v)) else v)
                for k, v in zip(keys, vals)
            }

            return ret

        ## usuniecie nadmiarowego przecinku przed }
        msgDict = removeAddComma(msgDict)
        ## usuniecie spacji
        msgDict = msgDict.replace(" ", "")
        ##
        Dictionary = transformToDict(msgDict)
        return Dictionary

    @classmethod
    def ReadComandTags(cls, TagDictMsg) -> Tuple[str, Dict[str, str|Dict[str, Any]]]:
        ## odczyt tagu wraz ze słownikiem z parametrami
        try:
            tag, msgDict = TagDictMsg.split( cls.TAG.HASH )

            Dictionary = cls.conver_MsgDict_2_Dict(msgDict=msgDict)

            return tag, Dictionary
        except Exception as e:
            LOG.print( f"<ERR> Message contain # {e}" )
            return None, None


    @classmethod
    def WriteComandTags(cls, tag, *command )->str:
        ## jeśli zostalu dodadane komendy to wpisywane zostaje do tagu
        cmds = "" if len(command)==0 else cls.CMD.SEPARATOR.join(
            map(str, [
                ( c.value if hasattr(c, 'value') else str(c) )
                for c in command
                ]
            )
        ) + cls.CMD.SEPARATOR

        return tag + cls.TAG.HASH + cmds
