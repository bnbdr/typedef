from abc import ABCMeta, abstractmethod
from typedef.constants import Arch
from typedef.errors import PragmaValueMissing, UnsupportedPragmaPack

pack_stack = []


class PragmaStack(object):
    __metaclass__ = ABCMeta

    def __init__(self, default_val):
        self._stack = []
        self._default = default_val
        self._waiting = True
        self._next_val = None

    def __call__(self, v):
        self._validate(v)  # should raise ValueError

        self._waiting = False
        self._next_val = v
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._waiting = True
        self.pop()

    def __enter__(self):
        if self._waiting:
            raise PragmaValueMissing('missing pragma value')

        self._stack.append(self._next_val)

    @abstractmethod  # TODO: maybe allow non validations?
    def _validate(self, v):
        pass

    @property
    def Current(self):
        try:
            return self._stack[-1]
        except IndexError:
            return self._default

    def pop(self):
        try:
            return self._stack.pop()
        except IndexError:
            return self._default

    def push(self, v):
        self._validate(v)
        self._stack.append(v)


class PragmaPack(PragmaStack):
    Unknown = None
    Infer = 0
    Tight = 1
    x86 = 4
    x64 = 8
    Os = [x86, x64][Arch.Os]
    Options = [2 ** i for i in range(5)]
    Interpreter = [x86, x64][Arch.Interpreter]

    def __init__(self):
        super(PragmaPack, self).__init__(self.Infer)

    def _validate(self, v):
        if v is not PragmaPack.Infer and v not in self.Options:
            raise UnsupportedPragmaPack('unsupported pack value')


pack = PragmaPack()
