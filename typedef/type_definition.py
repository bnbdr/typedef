import struct as pystruct
from collections import Counter
from numbers import Number

try:
    from itertools import izip
except ImportError:
    izip = zip

from string import ascii_letters
from typedef.type_creation import *
from typedef.core_utils import *
from typedef.pragma import pack
from typedef.errors import UnsupportedInitializationMethod, TypeMismatch, BadAccessorName
from typedef.utils import str_buffer_types

permissable_name_prefix = set(ascii_letters + '_')
defined_types = {}


def define_struct(name, members, accessor):
    return StructMeta(name, (StructType,), members, accessor)


def define_union(name, members, accessor):
    return UnionMeta(name, (UnionType,), members, accessor)


def define_array(name, t, count):
    return ArrayMeta(name, (ArrayType,), t, count)


def define_simple_type(name, sizes, signed, end):
    class_desc = (name, sizes, signed, end)
    if class_desc in defined_types:  # TODO: check global flag if should use the defined_Types cache or not
        return defined_types[class_desc]

    new_cls = SimpleMeta(name, (SimpleType,), sizes, signed, end)
    defined_types[class_desc] = new_cls
    return new_cls


class ArrayableMeta(type):
    def __getitem__(cls, count):
        return define_array('array.{}.{}'.format(count, cls.__name__), cls, count)


class SimpleMeta(ArrayableMeta):
    Masks = dict([(s, 2 ** (s * 8) - 1) for s in [1, 2, 4, 8, 16]])

    def __new__(mcs, name, parents, sizes, signed, end, default=0, frmt=None):
        used_members = {
            '__frmt__': frmt or SimpleMeta._get_frmts(sizes, signed, end),
            '__align__': sizes,
            '__end__': end,
            '__signed__': signed,
            '__size__': sizes,
            '__default__': default
        }

        cls = super(SimpleMeta, mcs).__new__(mcs, name, parents, {'__slots__': set(used_members.keys())})
        for k in used_members:
            v = used_members[k]
            setattr(cls, k, v)

        return cls

    @staticmethod
    def _get_format_for_arch(sizes, signed, end, arch):
        end = {Endian.Little: '<', Endian.Big: '>'}[end]
        sgn = int(signed)  # __signed__ is bool, so unsigned is 1
        frmt = {1: 'Bb', 2: 'Hh', 4: 'Ii', 8: 'Qq'}[sizes[arch]][sgn]
        return end + frmt

    @staticmethod
    def _get_frmts(sizes, signed, end):
        return (SimpleMeta._get_format_for_arch(sizes, signed, end, Arch.x86),
                SimpleMeta._get_format_for_arch(sizes, signed, end, Arch.x64))

    def __init__(mcs, name, bases, cls_members, _, __):
        super(SimpleMeta, mcs).__init__(name, bases, cls_members)

    def __neg__(cls):
        return define_simple_type(cls.__name__, cls.__size__, signed=cls.__signed__, end=Endian.Little)

    def __pos__(cls):
        return define_simple_type(cls.__name__, cls.__size__, signed=cls.__signed__, end=Endian.Big)

    def __invert__(cls):
        return define_simple_type(cls.__name__, cls.__size__, signed=True, end=cls.__end__)

    def __abs__(cls):
        return define_simple_type(cls.__name__, cls.__size__, signed=False, end=cls.__end__)

    def __call__(self, b=None, target=None, *args, **kwargs):

        if target is None and len(set(self.__size__)) == 2:  # size differ on archs
            raise ArchDependentType('requires arch on simpletype __call__')
        target = target or 0
        frmt = self.__frmt__[target]

        if b is None:
            return self.__default__

        if isinstance(b, Number):
            if not self.__signed__:
                s = self.__size__[target]
                b = b & SimpleMeta.Masks[s]
            return pystruct.pack(frmt, b)

        if type(b) not in str_buffer_types and type(b) is type(''):
            raise BadBufferInput('input string should be one of the following: {}'.format(str_buffer_types))

        if type(b) in str_buffer_types:
            return pystruct.unpack(frmt, b)[0]

        return pystruct.unpack(frmt, b.read(self.__size__[target]))[0]


class ComplexMeta(type):
    def __getattr__(self, item):
        # TODO: test this with namless unions
        if item not in self.__names__:
            raise AttributeError('`{}` type has no attribute `{}`'.format(self.__name__, item))
        return self.__types__[self.__names__.index(item)]

    def __repr__(cls):
        o = cls.__name__
        for internal_mem in cls.__slots__:
            o += '\n\t{}: {}'.format(internal_mem, str(cls.__dict__[internal_mem]))

        return o

    def __str__(cls):
        return "<type `{}`>".format(cls.__name__)

    def __new__(mcs, name, parents, member_list, accessor=''):
        if type(member_list) not in [list, tuple]:
            raise UnsupportedInitializationMethod(
                'type `{}` is not supported; only list or tuple'.format(type(member_list)))
        if not member_list:
            raise UnsupportedInitializationMethod('requires field definitions')

        rvals_new = []
        new_membs = []
        for tn in member_list:
            if type(tn) in [tuple]:
                new_membs.append(tn)
            else:
                try:
                    if issubclass(tn, NamedContainer):  # RVALUE
                        n = tn.__accessor__  # :nameless or not
                        t = tn
                        rvals_new.append(n)
                        new_membs.append((t, n))
                    else:
                        raise UnsupportedInitializationMethod('input must be simple or complex type-definition')
                except TypeError:
                    raise UnsupportedInitializationMethod('unsupported input for type-member tuple')

        member_list = new_membs
        rvals = rvals_new

        max_t_size = max([t.__align__ for t, n in member_list])
        is_union = issubclass(mcs, UnionMeta)
        is_array = issubclass(mcs, ArrayMeta)
        pragma_pack = pack.Current if not is_array else 0

        sizes, children_offsets, children_tps, children_nms, unions_proxy = extract(member_list, pragma_pack, rvals,
                                                                                    is_union)
        if is_union:
            sizes = max_child_sizes(children_tps)

        align = (pragma_pack, pragma_pack) if pragma_pack and not is_array else max_t_size
        pad_size = get_padding_size(sizes[0], align[0]), get_padding_size(sizes[1], align[1])
        sizes = add_tuples(sizes, pad_size)
        used_members = {
            '__pad__': tuple(pad_size),
            '__machdep__': len(set(sizes)) == 2,
            '__align__': align,
            '__accessor__': accessor,
            '__names__': children_nms,
            '__types__': children_tps,
            '__offsets__': children_offsets,
            '__pack__': pragma_pack,
            '__size__': tuple(sizes),
            '__nunions__': unions_proxy
        }
        if accessor:
            ComplexMeta._check_names([accessor], used_members.keys())  # just to make sure
        
        should_check_names = [1 for p in parents if issubclass(p, NamedContainer) ]
        if should_check_names:
            ComplexMeta._check_names(children_nms, disallowed_names=used_members.keys())

        ComplexMeta._check_types(children_tps)
        cls_members = {
            '__slots__': tuple(
                list(used_members.keys()) + ['__weakref__', '__len__', '__values__', '__onchange__', '__arch__',
                                             '__buffer__', '__pass__', '__start__'])
        }

        cls = super(ComplexMeta, mcs).__new__(mcs, name, parents, cls_members)
        for k in used_members:
            v = used_members[k]
            setattr(cls, k, v)

        return cls

    @staticmethod
    def _check_types(tps):
        [0 if issubclass(t, TypeDefinition) else throw(TypeMismatch('unsupported member type {}'.format(t))) for
         t in tps]

    @staticmethod
    def _check_names(names, disallowed_names=()):
        bad_names = [k for k, v in Counter(names).items() if v > 1]
        if bad_names:
            raise BadAccessorName('found duplicate names overriding each other: {}'.format(bad_names))

        bad_names = [n for n in names if n.lower() in disallowed_names]
        if bad_names:
            raise BadAccessorName('{} override internal names'.format(bad_names))

        bad_names = [n for n in names if n[0] not in permissable_name_prefix or n[:2] == '__']
        if bad_names:
            raise BadAccessorName('{} have unsupported prefixes'.format(bad_names))

    def __init__(mcs, name, bases, attr, *args):
        super(ComplexMeta, mcs).__init__(name, bases, attr)

    def __iter__(self):
        return izip(self.__types__, self.__names__)


class StructMeta(ComplexMeta, ArrayableMeta):
    def __new__(mcs, name, parents, member_list, accessor):
        cls = super(StructMeta, mcs).__new__(mcs, name, parents, member_list, accessor)
        return cls

    def __init__(mcs, name, bases, attr, *args):
        super(StructMeta, mcs).__init__(name, bases, attr)


class UnionMeta(ComplexMeta, ArrayableMeta):
    def __new__(mcs, name, parents, member_list, accessor):
        cls = super(UnionMeta, mcs).__new__(mcs, name, parents, member_list, accessor)
        return cls

    def __init__(mcs, name, bases, attr, *args):
        super(UnionMeta, mcs).__init__(name, bases, attr)


class ArrayMeta(ComplexMeta):
    def __new__(mcs, name, parents, t, count):
        cls = super(ArrayMeta, mcs).__new__(mcs, name, parents, list(zip((t,) * count, ('',) * count)))
        cls.__align__ = t.__align__
        return cls

    def __init__(mcs, name, bases, t, count):
        super(ArrayMeta, mcs).__init__(name, bases, t, count)

    def __len__(self):
        return len(self.__types__)
