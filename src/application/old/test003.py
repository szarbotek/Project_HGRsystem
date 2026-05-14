class CCC:

    def __getattribute__(self, name):
        attr = super().__getattribute__(name)
        print("C", attr)

        if name == "print" and callable(attr):
            def new_print(*args, **kwargs):
                # najpierw wywołanie oryginalnego print (np. AAA.print)
                result = attr(*args, **kwargs)
                # potem wywołanie nadrzędnego print (FFF)
                print("CCC")
                return result

            return new_print
        return attr

class WWW:
    def __getattribute__(self, name):
        attr = super().__getattribute__(name)
        print("W",attr)

        if name == "print" and callable(attr):
            def new_print(*args, **kwargs):
                # najpierw wywołanie oryginalnego print (np. AAA.print)
                result = attr(*args, **kwargs)
                # potem wywołanie nadrzędnego print (FFF)
                print("WWW", self.x)
                return result
            return new_print
        return attr

class AAA(WWW, CCC):

    def __init__(self):
        super().__init__()
        self.x ="dogi"

    def print(self):
        print("AAA", self.x)

# Test
a = AAA()
a.print()