import weakref

try:
    from cStringIO import StringIO
except ImportError:
    from io import BytesIO as StringIO

try:
    from itertools import izip
except ImportError:
    izip = zip

from typedef.constants import *
from typedef.errors import TypeMismatch, ArchDependentType, BufferTooShort, UnsupportedInitializationMethod, \
    BadBufferInput
from typedef.utils import str_buffer_types
from typedef.constants import MAX_REPR_BYTE_PRINT


class TypeDefinition(object):
    # TODO: make abstract
    __slots__ = ()


class SimpleType(TypeDefinition):
    __slots__ = ()

    @classmethod
    def verify(cls, v, taget_arch):
        if isinstance(v, TypeContainer):
            raise TypeMismatch('cannot set complex type to simple type')
        cls(v, taget_arch)  # TODO: maybe throw good exception?


def onchange_logic(obj, offset, new_buffer, child_i, child_size=None):
    obj = obj()
    bio = obj.__buffer__

    if new_buffer is None:
        o_start = obj.__offsets__[child_i][obj.__arch__] + offset
        o_s = child_size or obj.__types__[child_i].__size__[obj.__arch__]
        bio.seek(o_start)
        return bio.read(o_s)

    target_o = obj.__offsets__[child_i][obj.__arch__] + offset if child_i is not None else offset
    target_o_end = target_o + len(new_buffer)
    bio.seek(target_o)
    bio.write(new_buffer)
    bio.flush()

    for i, os in enumerate(obj.__offsets__):
        o = os[obj.__arch__]
        t = obj.__types__[i]
        s = t.__size__[obj.__arch__]
        bio.seek(o)
        
        if o <= target_o <o+s:
            assert s >= len(new_buffer), 'new buffer overflows its containing type'
            obj.__values__[i] = t(bio.read(s) if issubclass(t, SimpleType) else bio, target=obj.__arch__,
                                  prnt=weakref.ref(obj),
                                  idx=i)
    bio.seek(obj.__start__)


def get_buf(self):
    if self.__buffer__ is None:
        return self.__onchange__(0, None, None)
    self.__buffer__.seek(self.__start__)
    return self.__buffer__.read()


class TypeContainer(TypeDefinition):
    __slots__ = ()

    def __dir__(self):
        return list(set(self.__names__))

    def __del__(self):
        if hasattr(self, '__pass__') and self.__pass__ == F_SYNC:
            self.__buffer__.close()

    def __str__(self):  # py2
        return get_buf(self)

    def __bytes__(self):  # py3
        return get_buf(self)

    def __repr__(self):
        b = get_buf(self)
        suffix = ''
        if len(b) > MAX_REPR_BYTE_PRINT:
            count_remaining = len(b) - MAX_REPR_BYTE_PRINT
            b = b[:MAX_REPR_BYTE_PRINT]
            suffix = ' ...(%d truncated)' % count_remaining
        return " ".join('%02x' % (ord(c) if isinstance(c, *str_buffer_types) else c) for c in b) + suffix

    def __init__(self, b, target, prnt, idx, passthrough):
        if self.__machdep__ and target == Arch.Unknown:
            raise ArchDependentType('requires target machine architecture for pragma pack')
        target = target or 0  # if no need for target-arch get the first index of sizes (they're they same anywas)
        totatl_s = self.__size__[target]

        super(TypeContainer, self).__setattr__('__values__', [])
        if prnt:
            onchange = lambda _o, _b, _i, idx=idx, wself=weakref.ref(self): (
                                                                                prnt().__onchange__(
                                                                                    wself().__offsets__[_i][
                                                                                        target] + _o if _i is not None else _o,
                                                                                    _b, idx) or [])[
                                                                            :wself().__types__[_i].__size__[
                                                                                target] if _i is not None else None]
            super(TypeContainer, self).__setattr__('__buffer__', None)
        else:
            super(TypeContainer, self).__setattr__('__buffer__',
                                                   StringIO())
            onchange = lambda _o, _b, _i, wself=weakref.ref(self): onchange_logic(wself, _o, _b, _i)

        # TODO: use global init char? or make per member type

        super(TypeContainer, self).__setattr__('__start__', 0)
        super(TypeContainer, self).__setattr__('__pass__', passthrough)
        super(TypeContainer, self).__setattr__('__onchange__', onchange)
        super(TypeContainer, self).__setattr__('__arch__', target)
        super(TypeContainer, self).__setattr__('__len__', lambda wself=weakref.ref(self): len(wself().__values__))

        if not b:
            [
                self.__values__.append(t(target=target, prnt=weakref.ref(self), idx=i)) for i, t in
                enumerate(self.__types__)
                ]
            if not prnt:
                self.__buffer__.write(b'\x00' * totatl_s)
            return

        if type(b) not in str_buffer_types and type(b) is type(''):
            raise BadBufferInput('input string should be one of the following: {}'.format(str_buffer_types))
        f = b
        if type(b) in str_buffer_types:
            if len(b) < totatl_s:
                raise BufferTooShort(
                    'buffer too short, {} requires {}, received {}'.format(self.__class__.__name__, totatl_s, len(b)))
            # raw binary string
            f = StringIO(b)
            start = f.tell()

        else:  # file interface
            start = f.tell()
            if passthrough and not prnt:
                # test its ok to read write; `mode` attribute does not exist on StrigIOs (ignore if prnt passed this handle)
                test_byte = f.read(1)  # there has to be at least 1 byte ready
                f.seek(start)
                f.write(test_byte)

            if passthrough:
                super(TypeContainer, self).__setattr__('__buffer__', f)
                super(TypeContainer, self).__setattr__('__start__', start)

        raw_buffer = b''
        this_is_union = issubclass(self.__class__, UnionType)
        if this_is_union:
            raw_buffer = f.read(totatl_s)
            f.seek(start)
        nuni_ignore = []
        for i, t in enumerate(self.__types__):  # TODO: work using F and read
            isnuni = self.__names__[i] in self.__nunions__
            if isnuni:
                n = self.__names__[i]
                if n not in nuni_ignore:
                    u = self.__nunions__[n]
                    nuni_ignore.extend(u.__names__)
                    s = u.__size__[target]
                    d = f.read(s)
                    assert len(d) == s, 'tried reading {}, got {}'.format(s, len(d))
                    raw_buffer += d

            s = t.__size__[target]
            o = self.__offsets__[i][target]

            if not this_is_union and not isnuni:
                if len(raw_buffer) < o:
                    raw_buffer += f.read(o - len(raw_buffer))

            f.seek(start + o)
            rv = f.read(s)
            assert len(rv) == s
            self.__values__.append(t(rv, target=target, prnt=weakref.ref(self), idx=i))
            if not this_is_union and not isnuni:
                raw_buffer += rv

        raw_buffer += f.read(self.__pad__[target])

        if not prnt and not passthrough:
            self.__buffer__.seek(0)
            self.__buffer__.write(raw_buffer)


class UnnamedContainer(TypeContainer):
    __slots__ = ()

    def __init__(self, b, target, prnt, idx, passthrough):
        vs = []
        if type(b) in [tuple, list]:
            vs = b
            b = ''

        super(UnnamedContainer, self).__init__(b, target, prnt, idx, passthrough)
        for i, v in enumerate(vs):
            self[i] = v


def _getvalue(obj, tp, value):
    if issubclass(tp, TypeContainer):
        if type(value) in [dict, list, tuple]:  # for arrays or structs
            nv = tp(value, target=obj.__arch__)
            value = bytes(nv)  # must not pass claback otherwise will screw up the buffer
        elif isinstance(value, tp):
            value = bytes(value)
        elif type(value) in str_buffer_types:
            pass
        else:
            raise TypeMismatch('type mismatch for: {}, {} '.format(tp, type(value)))

    else:  # issubclass(tp, SimpleType)
        tp.verify(value, obj.__arch__)  # should assert

        if type(value) not in str_buffer_types:
            value = tp(value, target=obj.__arch__)

    return value


class ArrayType(UnnamedContainer):  #
    __slots__ = ()

    def __init__(self, b='', target=Arch.Unknown, mode=F_COPY, prnt=None, idx=None,
                 ):  # todo add buffer option, pack
        super(ArrayType, self).__init__(b, target, prnt, idx, mode)

    def __getitem__(self, idx):
        return self.__values__[idx]

    def __setitem__(self, idx, value):
        idx = int(idx)
        tp = self.__types__[idx]

        value = _getvalue(self, tp, value)
        self.__onchange__(0, value, idx)  # this would return buffer

    def __iter__(self):
        return izip(range(len(self.__values__)), self.__values__)


class NamedContainer(TypeContainer):
    __slots__ = ()

    def __iter__(self):
        return izip(self.__names__, self.__values__)

    def __init__(self, b='', target=Arch.Unknown, prnt=None, idx=None, passthrough=F_COPY):
        """
        """
        init_dict = {}
        if type(b) in [dict]:
            init_dict = b
            b = ''  # this will make sure all values are default, then override according to init_dict later

        super(NamedContainer, self).__init__(b, target, prnt, idx, passthrough)
        for k in init_dict:
            v = init_dict[k]
            self.__setattr__(k, v)

    def __setattr__(self, key, value):
        if key not in self.__names__:
            raise AttributeError('`{}` not defined in `{}`'.format(key, self.__class__))

        idx = self.__names__.index(key)
        tp = self.__types__[idx]
        
        value = _getvalue(self, tp, value)
        self.__onchange__(0, value, idx)  # this would return buffer
        
    def __getattr__(self, item):
        if item not in self.__names__:
            raise AttributeError('`{}` not defined in `{}`'.format(item, self.__class__))

        idx = self.__names__.index(item)
        return self.__values__[idx]


class StructType(NamedContainer):
    __slots__ = ()

    def __init__(self, b='', target=Arch.Unknown, mode=F_COPY, prnt=None, idx=None):
        if type(b) in [list, tuple]:
            raise UnsupportedInitializationMethod(
                'struct cannot be initialized using a list or tuple; only buffer or dict')

        super(StructType, self).__init__(b, target, prnt, idx, mode)


class UnionType(NamedContainer):
    __slots__ = ()

    def __init__(self, b='', target=Arch.Unknown, mode=F_COPY, prnt=None, idx=None):
        if type(b) in [dict, list, tuple]:
            raise UnsupportedInitializationMethod('union cannot be initialized using a dict/list/tuple; only buffer')
        super(UnionType, self).__init__(b, target, prnt, idx, mode)
