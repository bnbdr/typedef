from .type_definition import define_simple_type, define_array, define_struct, define_union
from .constants import Endian


def sizeof(container):
    return container.__size__[container.__arch__]


def struct(members, name=''):
    accessor = name
    if not name:
        name = 'nameless_struct'
    return define_struct(name, members, accessor)


def union(members, name=''):
    accessor = name
    if not name:
        name = 'nameless_union'
    return define_union(name, members, accessor)


def array(t, count):
    name = 'array.{}.{}'.format(count, t.__name__)
    return define_array(name, t, count)


def define(name, sizes, signed=False, end=Endian.Little):
    sizes = sizes if type(sizes) in [tuple, list] else (sizes,) * 2
    return define_simple_type(name, sizes, signed, end)

