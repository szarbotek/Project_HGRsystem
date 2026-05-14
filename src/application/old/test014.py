from typing import Dict, Tuple

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

    ## usuniecie nadmiarowego przeciku przed }
    msgDict = removeAddComma(msgDict)
    ## usuniecie spacji
    msgDict = msgDict.replace(" ", "")
    ##
    Dictionary = transformToDict(msgDict)
    return Dictionary


t = "{ dataUnit:{ Tool:tool0, WorkObject:wobj0, PayLoad:load0, Status:Stopped, Pos:[286.27,0.02,476.4201], Speed:100,  }, msg:Wrong option,  }"
r = conver_MsgDict_2_Dict(t)
print(r)
