import inspect
import uuid
from sys import version_info

if version_info[0] < 3:
    str_buffer_types = [str]
else:
    str_buffer_types = [bytes]


def add_tuples(a, b):
    return list(map(sum, list(zip(a, b))))


def throw(x):
    raise x


def random_name_suffix():
    return format(uuid.uuid4().hex)


def get_padding_size(cur_offset, pragma_pack):
    if cur_offset == 0:
        return 0

    if cur_offset <= pragma_pack:
        return pragma_pack - cur_offset
    return 0 if cur_offset % pragma_pack == 0 else (int(cur_offset / pragma_pack) + 1) * pragma_pack - cur_offset


def get_caller_name():
    frame = inspect.currentframe().f_back.f_back
    mod_name = frame.f_globals['__package__'] or frame.f_globals['__name__']
    return mod_name


def paddify(size, machine_arch, pragma_pack, t):
    return size + get_padding_size(size, pragma_pack or t.__align__[machine_arch])
