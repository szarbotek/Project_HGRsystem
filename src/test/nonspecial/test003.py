from datetime import datetime


class LOGI:

    msg = ""

    @staticmethod
    def print(msg):
        print(msg)
        LOGI.msg += msg

    def __init__(self):
        print("hello")
        LOGI.msg += "===[LOGI] RAPORT GENERATET AT: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def __del__(self):
        print("bye", LOGI.msg)

L = LOGI()