from __future__ import print_function
import json
from typedef import *

S = struct([
    (DWORD, 'd'),
    (BYTE[4], 'bs'),
    union([
        (DWORD, 'build'),
        struct([
            (WORD, 'mj'),
            (WORD, 'mn')
        ], 'inn')
    ])
])

s = S(b'\xff\xff\xff\xffaaaa\x01\x00\x02\x00')
print('dumping json for: {}'.format(repr(s)))
print(json.dumps(s, cls=TypeEncoder, indent=2))
