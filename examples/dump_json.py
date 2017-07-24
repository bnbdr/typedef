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
            (WORD, 'mn'),
            struct([
                (BYTE, 'b1'),
                (BYTE, 'b2')
            ], 'even_inner')
        ], 'inn')
    ])
])

s = S(b'\xff\xff\xff\xffaaaa\x01\x00\x02\x00' + '\x00' + '\x02'+'!'*2) # two '!' for padding, main struct must be aligned to 4
print('dumping json for: {}'.format(repr(s)))
print(json.dumps(s, cls=TypeEncoder, indent=2))
