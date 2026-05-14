
from typing import Any, List, Tuple, TypedDict

class CircularBuffer:
    """
        Circular Buffer - klasa posiada N miejs określanych przy tworzeniu struktury.

        Elementy są dokładane poprzez self.put nowy elemnt jest dokładany na poczatek kolejki, natomiast jeśli wymiar
        kolejki miałby zostać zwiększony usuwany zostaje najstarszy element.


    """

    def __init__(self, max_lenght: int = 10):

        self._max_len = max_lenght
        self.FLAG_full_stack = False
        self.buffer: List[Any] = []

    def put(self, element ):
        self.buffer.insert( 0, element )
        if len(self.buffer) > self._max_len or self.FLAG_full_stack:
            self.throw()
            self.FLAG_full_stack = True

        self.first = self.buffer[0]
        self.last = self.buffer[-1]

    def throw(self):
        ret = self.buffer.pop(-1)
        self.FLAG_full_stack = False
        return ret

    def clear(self):
        ret = self.buffer.clear()
        self.FLAG_full_stack = False
        self.first = None
        self.last = None

    def pop(self, index):
        ret = self.buffer.pop(index)
        self.FLAG_full_stack = False
        self.first = self.buffer[0]
        self.last = self.buffer[-1]
        return ret

    def get_buffer_index(self, index):
        ret = None
        try:
            ret =  self.slice(index, index+1)
            if ret is None or ret is []: return ret
            return ret[0] if isinstance(ret, list) else ret
        except Exception as e:
            print(e, ret)
            return None

    def slice(self, start_index: int, finish_index: int = None, step: int = 1):
        if finish_index is None: finish_index = start_index + 1
        if ((-self._max_len) <= start_index <= self._max_len-1) and ((-self._max_len) <= finish_index <= self._max_len-1):
            return self.buffer[start_index : finish_index : step]
        else:
            return None

    def get_buffer(self):
        return self.buffer.copy()

    def get_reverse_buffer(self):
        brr = self.buffer.copy()
        brr.reverse()
        return brr

    def __len__(self):
        return len(self.buffer)

    def __iter__(self):
        return iter(self.buffer)

    def __str__(self):
        return str(self.buffer)

from typing import TypedDict, Any

class T_LeftRight(TypedDict):
    """
        Right: Any
        Left: Any
    """
    Right: Any
    Left: Any