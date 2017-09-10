import json
from collections import OrderedDict
from typedef.type_creation import NamedContainer, UnnamedContainer


class TypeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, NamedContainer):
            return OrderedDict(zip(obj.__names__, obj.__values__))

        if isinstance(obj, UnnamedContainer):
            return obj.__values__
        return json.JSONEncoder.default(self, obj)
