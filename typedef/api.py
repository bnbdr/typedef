from typedef.type_definition import define_simple_type, define_array, define_struct, define_union
from typedef.constants import Endian, Arch
from typedef.errors import ArchDependentType, MissingField


def sizeof(t, target_arch=Arch.Unknown):
    """
       return the number of bytes the complex-type instance represents
       :param t: instance of struct/union/array
       :param target_arch: target architecture, if required by type
       :return: number of bytes the container has
   """

    sizes = t.__size__
    if sizes[0] == sizes[1]:
        return sizes[0]

    try:
        arch = t.__arch__ + 0
    except (AttributeError, TypeError):
        arch = target_arch

    if arch is Arch.Unknown:
        raise ArchDependentType('type size depends on target arch')

    return sizes[arch]


def offsetof(mem_name, t, target_arch=Arch.Unknown):
    """
       return the offset within the container where `member` can be found
       :param mem_name: string, name of member
       :param t: instance of struct/union/array
       :param target_arch: target architecture, if required by type
       :return: number of bytes the container has
   """

    try:
        offsets = t.__offsets__[t.__names__.index(mem_name)]
    except:
        raise MissingField('`{}` cannot be found in type {}'.format(mem_name, repr(t)))

    if offsets[0] == offsets[1]:
        return offsets[0]

    try:
        arch = t.__arch__ + 0
    except (AttributeError, TypeError):
        arch = target_arch

    if arch is Arch.Unknown:
        raise ArchDependentType('type offset depends on target arch')

    return offsets[arch]


def struct(members, name=''):
    """
        define a struct
        :param members: list of type-name tuples, or copmlex types (for anonymous/rval structs/unions)
        :param name: name of the struct.
                     if the struct is a nested definition, this will be the accessor(attribute name) for the struct.
        :return: a new struct
         definition
    """
    accessor = name
    if not name:
        name = 'nameless_struct'
    return define_struct(name, members, accessor)


def union(members, name=''):
    """
        define a union
        :param members: list of type-name tuples, or copmlex types (for anonymous/rval structs/unions)
        :param name: name of the union
                     if the union is a nested definition, this will be the accessor(attribute name) for the union.
        :return: a new union definition
    """
    accessor = name
    if not name:
        name = 'nameless_union'
    return define_union(name, members, accessor)


def array(t, count):
    """
        define an array of a specific type
        :param t: type for the array
        :param count: size of the array
        :return: a new array type
    """
    name = 'array.{}.{}'.format(count, t.__name__)
    return define_array(name, t, count)


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
    sizes = sizes if type(sizes) in [tuple, list] else (sizes,) * 2
    return define_simple_type(name, sizes, signed, end)
