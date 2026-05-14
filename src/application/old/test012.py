

class DYNAMIC:
    class MetaNumerator(type):
        def __str__(cls):
            return str(cls.value)

    class NUMERATOR(metaclass=MetaNumerator):
        value = 0
        range = 5

        @classmethod
        def increment(cls):
            cls.value += 1
            if cls.value > cls.range:
                cls.value = 0

        @classmethod
        def decrement(cls):
            cls.value -= 1
            if cls.value < 0:
                cls.value = cls.range

        def __str__(self):
            return str(self.value)


print( str(DYNAMIC.NUMERATOR) )