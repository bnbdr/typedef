import platform

MAX_REPR_BYTE_PRINT = 200


class Endian:
    Reserved = 0  # TODO: network = big
    Little = 1
    Big = 2


class Arch:
    Unknown = None
    x86 = 0
    x64 = 1
    Os = x64 if 'AMD64' == platform.machine().upper() else x86
    Interpreter = x86 if '32bit' == platform.architecture('')[0].lower() else x64
    Options = [x86, x64]


class Machine:
    PointerSize = [4, 8]


# if input has file interface (file object / StringIO):
F_COPY = 0  # DEFAULT. copy the buffer
F_SYNC = 3  # hold reference to the buffer and use it directly
