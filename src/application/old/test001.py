

class FFF:
    def print(self, text):

        print("To jest print z Frame:", text)

class WWW(FFF):
    def __getattribute__(self, name):
        attr = super().__getattribute__(name)
        if name == "print" and callable(attr):
            def new_print(*args, **kwargs):
                # wywołanie print z FFF automatycznie
                FFF.print(self, "WWW")
                # następnie wywołanie oryginalnego print
                return attr(*args, **kwargs)
            return new_print
        return attr


class AAA(WWW):

    def print(self):

        print("AAA")

    

# Test
a = AAA()
a.print()