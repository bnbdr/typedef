"""
A somewhat convenient package for packing and unpacking structs, unions, and arrays using C-like syntax
"""
import typedef.api
import typedef.errors
from .primitives import *
from .constants import Endian, Arch, F_SYNC, F_COPY
from .json_encoder import TypeEncoder
from .pragma import pack

version = (0, 9, 0, 5)
__version__ = '.'.join(map(str, version))
__description__ = 'A somewhat convenient package for packing and unpacking structs, unions, and arrays using C-like syntax'


def sizeof(container):
    """
    return the number of bytes the complex-type instance represents
    :param container: instance of struct/union/array
    :return: number of bytes the container has
    """
    return api.sizeof(container)


def struct(members, name=''):
    """
    define a struct
    :param members: list of type-name tuples, or copmlex types (for anonymous/rval structs/unions)
    :param name: name of the struct.
                 if the struct is a nested definition, this will be the accessor(attribute name) for the struct.
    :return: a new struct
     definition
    """
    return api.struct(members, name)


def union(members, name=''):
    """
    define a union
    :param members: list of type-name tuples, or copmlex types (for anonymous/rval structs/unions)
    :param name: name of the union
                 if the union is a nested definition, this will be the accessor(attribute name) for the union.
    :return: a new union definition
    """
    return api.union(members, name)


def array(t, count):
    """
    define an array of a specific type
    :param t: type for the array
    :param count: size of the array
    :return: a new array type
    """
    return api.array(t, count)


def define(name, sizes, signed=False, end=Endian.Little):
    """
    define a new simple-type
    :param name: name of the type, will be shown when printing the type ow when used in arrays
    :param sizes: an integer specifying the size of the type.
                  if its size vary between the two architectures, a tuple of sizes should be supplied
    :param signed: signed / unsigned
    :param end: little / big endianess
    :return: a new simple type
    """
    return api.define(name, sizes, signed, end)
