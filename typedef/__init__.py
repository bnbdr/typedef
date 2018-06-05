"""
Conveniently handle structs, unions, and arrays
"""
import typedef.api
import typedef.errors
import typedef.pragma
from typedef.api import *
from typedef.constants import Endian, Arch, F_SYNC, F_COPY
from typedef.primitives import *

version = (0, 9, 0, 7)
__version__ = '.'.join(map(str, version))
__description__ = 'Conveniently handle structs, unions, and arrays'
__all__ = ['pragma', 'Endian', 'Arch', 'F_SYNC', 'F_COPY', 'errors', 'sizeof', 'offsetof', 'struct',
           'union',
           'array', 'define', 'BYTE', 'WORD', 'DWORD', 'QWORD', 'HALF_PTR', 'PVOID', 'SIZE_T', 'SSIZE_T']
