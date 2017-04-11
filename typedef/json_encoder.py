import json
from collections import OrderedDict
from typedef.type_creation import NamedContainer, UnnamedContainer, UnionType


class TypeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, NamedContainer):
            o = OrderedDict()
            o['type'] = 'union' if isinstance(obj, UnionType) else 'struct'
            if obj.__accessor__:
                o['name'] = obj.__accessor__
            o['attributes'] = OrderedDict(zip(obj.__names__, obj.__values__))
            return o

        if isinstance(obj, UnnamedContainer):
            return obj.__values__
        return json.JSONEncoder.default(self, obj)
