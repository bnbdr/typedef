from typedef.constants import Arch
from typedef.utils import *
from typedef.type_creation import TypeContainer, NamedContainer, UnionType, StructType


def get_padded_new_offsets(t, curr_offsets, last_sizes, pragma_pack):
    return (paddify(add_tuples(curr_offsets, last_sizes)[Arch.x86], Arch.x86, pragma_pack, t),
            paddify(add_tuples(curr_offsets, last_sizes)[Arch.x64], Arch.x64, pragma_pack, t))


def add_memb_get_size(mt, mn, tps, nms):
    nms.append(mn)
    tps.append(mt)
    return mt.__size__


def extract(membs, pragma_pack, rvalues=(), is_union=False):
    children_tps = []
    children_nms = []
    offsets = []
    last_sizes = (0, 0)
    curr_offsets = (0, 0)
    value_proxy = {}

    handle_memb = lambda mt, mn: add_memb_get_size(mt, mn, children_tps, children_nms)

    for t, n in membs:
        curr_offsets = (0, 0) if is_union else get_padded_new_offsets(t, curr_offsets, last_sizes, pragma_pack)
        if n not in rvalues:
            offsets.append(curr_offsets)
            last_sizes = handle_memb(t, n)
            continue

        else:  # RVAL
            assert issubclass(t, TypeContainer), '{} cannot be RVAL container'.format(t)

            is_named = not (issubclass(t, NamedContainer) and t.__accessor__ == '')
            if is_named:
                # rval, not nameless, force pragma pack
                offsets.append(curr_offsets)
                last_sizes = handle_memb(t, n)
                continue

            else:  # nameless
                if issubclass(t, UnionType):
                    for ut, un in t:
                        value_proxy[un] = t
                        offsets.append(curr_offsets)  # not adding size to offset since its union
                        last_sizes = handle_memb(ut, un)
                    continue

                elif issubclass(t, StructType):  # struct
                    # TODO: should extend value proxy here if it exists in t (also in union)
                    if is_union:  # init the first member to the beginning of the union
                        curr_offsets = (0, 0)
                        last_sizes = (0, 0)

                    inner_st_last_size = (0, 0) 
                    
                    for st, sn in t:
                        curr_offsets = get_padded_new_offsets(st, curr_offsets, inner_st_last_size, pragma_pack)
                        inner_st_last_size = handle_memb(st, sn)
                        offsets.append(curr_offsets)
                    
                    last_sizes = inner_st_last_size
                    continue
    sizes = add_tuples(curr_offsets, last_sizes)

    return sizes, offsets, children_tps, children_nms, value_proxy


def max_child_sizes(children):
    return max([tuple(ut.__size__) for ut in children])
