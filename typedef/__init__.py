"""
A somewhat convenient package for packing and unpacking structs, unions, and arrays using C-like syntax
"""
import typedef.api
import typedef.errors
from .primitives import *
from .constants import Endian, Arch, F_SYNC, F_COPY
from .json_encoder import TypeEncoder
from . import pragma
from .api import *

version = (0, 9, 0, 5)
__version__ = '.'.join(map(str, version))
__description__ = 'A somewhat convenient package for packing and unpacking structs, unions, and arrays using C-like syntax'
__all__ = ['pragma', 'TypeEncoder', 'Endian', 'Arch', 'F_SYNC', 'F_COPY', 'errors', 'sizeof', 'offsetof', 'struct',
           'union',
           'array', 'define', 'BYTE', 'WORD', 'DWORD', 'QWORD', 'HALF_PTR', 'PVOID', 'SIZE_T', 'SSIZE_T']
