from base import *


class Struct(TypedefTestCase):

    def test_overriding_member_names(self):
        with self.assertRaises(BadAccessorName) as cm:
            BB = struct(
            [
                (DWORD, 'a'),
                struct(
                    [
                        (DWORD, 'aa'),
                        (DWORD, 'aa'),
                    ])
            ]
        )

        self.assertEqual(cm.exception.args[0], "found duplicate names overriding each other: ['aa']")
        

    def test_nameless_child_struct_in_offset(self):
        S = struct(
            [
                (DWORD, 'a'),
                struct(
                    [
                        (DWORD, 'aa'),
                    ])
            ]
        )
        self.assertEqual(S.__size__, (8,8))
        BB = struct(
            [
                (DWORD, 'a'),
                struct(
                    [
                        (DWORD, 'aa'),
                        (DWORD, 'bb'),
                    ])
            ]
        )
        self.assertEqual(BB.__size__, (12,12))
        
        with pragma.pack(8):
            BB = struct(
                [
                    (DWORD, 'a'),
                    struct(
                        [
                            (DWORD, 'aa'),
                            (DWORD, 'bb'),
                        ])
                ]
            )

        self.assertEqual(BB.__size__, (24,24))
        self.assertEqual(BB.__offsets__, [(0,0),(8,8),(16,16)])
        
    def test_complex_with_pack(self):
        with pragma.pack(4):
            S = struct([
                (BYTE, 'b'),
                (DWORD, 'd'),
                struct([
                    (BYTE[10], 'bs'),
                    (struct([
                        (WORD, 'w'),
                        (PVOID, 'p'),
                        (QWORD, 'q'),
                    ])[3], 'ar')
                ], 'inn')
            ])

        bf = b'c!!!\x00\x00\x00\x00' + \
             b'1' * 10 + b'!' * 2 + \
             b'bb~~\x00\xFF\xFF\xFF\xFF\xFF\xFF\x0012345678' + \
             b'bb~~\x01\xFF\xFF\xFF\xFF\xFF\xFF\x01abcdefgh' + \
             b'bb~~\x02\xFF\xFF\xFF\xFF\xFF\xFF\x02ABCDEFGH'

        bf32 = b'c!!!\x00\x00\x00\x00' + \
               b'1' * 10 + b'!' * 2 + \
               b'bb~~\x00\xFF\xFF\x0012345678' + \
               b'bb~~\x01\xFF\xFF\x01abcdefgh' + \
               b'bb~~\x02\xFF\xFF\x02ABCDEFGH'

        s = S(bf, target=Arch.x64)

        self.assertEqual(s.b, ord('c'))
        self.assertEqual(s.d, 0)
        self.assertEqual(bytes(s.inn.bs), b'\x31' * 10)
        self.assertEqual(s.inn.ar[0].w, WORD(b'bb'))
        self.assertEqual(s.inn.ar[0].p, 0x00FFFFFFFFFFFF00)
        self.assertEqual(s.inn.ar[0].q, 0x3837363534333231)

        self.assertEqual(s.inn.ar[1].w, WORD(b'bb'))
        self.assertEqual(s.inn.ar[1].p, 0x01FFFFFFFFFFFF01)
        self.assertEqual(s.inn.ar[1].q, 0x6867666564636261)

        self.assertEqual(s.inn.ar[2].w, WORD(b'bb'))
        self.assertEqual(s.inn.ar[2].p, 0x02FFFFFFFFFFFF02)
        self.assertEqual(s.inn.ar[2].q, 0x4847464544434241)

        s = S(bf32, target=Arch.x86)
        self.assertEqual(s.b, ord('c'))
        self.assertEqual(s.d, 0)
        self.assertEqual(bytes(s.inn.bs), b'\x31' * 10)
        self.assertEqual(s.inn.ar[0].w, WORD(b'bb'))
        self.assertEqual(s.inn.ar[0].p, 0x00FFFF00)
        self.assertEqual(s.inn.ar[0].q, 0x3837363534333231)

        self.assertEqual(s.inn.ar[1].w, WORD(b'bb'))
        self.assertEqual(s.inn.ar[1].p, 0x01FFFF01)
        self.assertEqual(s.inn.ar[1].q, 0x6867666564636261)

        self.assertEqual(s.inn.ar[2].w, WORD(b'bb'))
        self.assertEqual(s.inn.ar[2].p, 0x02FFFF02)
        self.assertEqual(s.inn.ar[2].q, 0x4847464544434241)

    def test_complex_with_union(self):
        S = struct([
            (BYTE, 'b'),
            (DWORD, 'd'),
            union([
                struct([
                    (BYTE[10], 'bs'),
                    (struct([
                        (WORD, 'w'),
                        (PVOID, 'p'),
                        (QWORD, 'q'),
                    ])[3], 'ar')
                ], 'inn')
            ])
        ])

        bf = b'c!!!\x00\x00\x00\x00' + \
             b'1' * 10 + b'!' * 6 + \
             b'bb~~!!!!\x00\xFF\xFF\xFF\xFF\xFF\xFF\x0012345678' + \
             b'bb~~!!!!\x01\xFF\xFF\xFF\xFF\xFF\xFF\x01abcdefgh' + \
             b'bb~~!!!!\x02\xFF\xFF\xFF\xFF\xFF\xFF\x02ABCDEFGH'

        bf32 = b'c!!!\x00\x00\x00\x00' + \
               b'1' * 10 + b'!' * 6 + \
               b'bb~~\x00\xFF\xFF\x0012345678' + \
               b'bb~~\x01\xFF\xFF\x01abcdefgh' + \
               b'bb~~\x02\xFF\xFF\x02ABCDEFGH'

        s = S(bf, target=Arch.x64)
        self.assertEqual(s.b, ord('c'))
        self.assertEqual(s.d, 0)
        self.assertEqual(bytes(s.inn.bs), b'\x31' * 10)
        self.assertEqual(s.inn.ar[0].w, WORD(b'bb'))
        self.assertEqual(s.inn.ar[0].p, 0x00FFFFFFFFFFFF00)
        self.assertEqual(s.inn.ar[0].q, 0x3837363534333231)

        self.assertEqual(s.inn.ar[1].w, WORD(b'bb'))
        self.assertEqual(s.inn.ar[1].p, 0x01FFFFFFFFFFFF01)
        self.assertEqual(s.inn.ar[1].q, 0x6867666564636261)

        self.assertEqual(s.inn.ar[2].w, WORD(b'bb'))
        self.assertEqual(s.inn.ar[2].p, 0x02FFFFFFFFFFFF02)
        self.assertEqual(s.inn.ar[2].q, 0x4847464544434241)

        s = S(bf32, target=Arch.x86)
        self.assertEqual(s.b, ord('c'))
        self.assertEqual(s.d, 0)
        self.assertEqual(bytes(s.inn.bs), b'\x31' * 10)
        self.assertEqual(s.inn.ar[0].w, WORD(b'bb'))
        self.assertEqual(s.inn.ar[0].p, 0x00FFFF00)
        self.assertEqual(s.inn.ar[0].q, 0x3837363534333231)

        self.assertEqual(s.inn.ar[1].w, WORD(b'bb'))
        self.assertEqual(s.inn.ar[1].p, 0x01FFFF01)
        self.assertEqual(s.inn.ar[1].q, 0x6867666564636261)

        self.assertEqual(s.inn.ar[2].w, WORD(b'bb'))
        self.assertEqual(s.inn.ar[2].p, 0x02FFFF02)
        self.assertEqual(s.inn.ar[2].q, 0x4847464544434241)

    def test_nameless_struct_child(self):
        S = struct([
            struct([
                (WORD, 'mn'),
                (WORD, 'mj')]
            ),
            (DWORD, 'build')
        ])
        self.assertEqual(S.__names__, ['mn', 'mj', 'build'])

        s = S(WORD(1) + WORD(2) + DWORD(3))
        self.assertEqual(s.mn, 1)
        self.assertEqual(s.mj, 2)
        self.assertEqual(s.build, 3)

    def test_nameless_union_child(self):
        S = struct([
            union([
                (WORD, 'mn'),
                (WORD, 'mj')]
            )
        ])
        self.assertEqual(S.__offsets__, [(0, 0), (0, 0)])
        self.assertEqual(S.__machdep__, False)
        self.assertEqual(S.__pack__, 0)
        self.assertEqual(S.__size__, WORD.__size__)
        self.assertEqual(S.__align__, WORD.__align__)

        b = b'\x01\x08'
        s = S(b)
        self.assertEqual(s.mn, s.mj)
        self.assertEqual(bytes(s), b)

    def test_union_child(self):
        S = struct([
            union([
                (WORD, 'mn'),
                (WORD, 'mj')
            ], 'u')
        ])

        self.assertEqual(S.__names__, ['u'])
        self.assertEqual(S.__pack__, 0)
        self.assertEqual(S.__align__, WORD.__align__)
        self.assertEqual(S.__size__, WORD.__size__)
        self.assertEqual(S.__size__, S.u.__size__)
        self.assertEqual(S.__offsets__, [(0, 0)])
        self.assertEqual(S.u.__offsets__, [(0, 0), (0, 0)])

        s = S(b'\x01\x02')
        self.assertEqual(s.u.mn, WORD(b'\x01\x02'))
        self.assertEqual(s.u.mn, s.u.mj)
        self.assertEqual(bytes(s), b'\x01\x02')
        self.assertEqual(bytes(s.u), b'\x01\x02')

    def test_set_child_struct(self):
        VERSION = struct([
            (WORD, 'mn'),
            (WORD, 'mj')
        ])

        S = struct([
            (VERSION, 'v'),
            (DWORD, 'bn')
        ])
        s = S()
        self.assertEqual(s.v.mn, 0)
        self.assertEqual(s.v.mj, 0)
        s.v = VERSION(b'\xFF\xFF\xFF\xFF')
        self.assertEqual(s.v.mn, 0xffff)
        self.assertEqual(s.v.mj, 0xffff)

    def test_fail_set_simple_with_complex(self):
        VERSION = struct([
            (WORD, 'mn'),
            (WORD, 'mj')
        ])

        S = struct([
            (VERSION, 'v'),
            (DWORD, 'bn')
        ])
        s = S()
        self.assertEqual(s.v.mn, 0)
        self.assertEqual(s.v.mj, 0)
        with self.assertRaises(TypeMismatch) as cm:
            s.bn = VERSION(b'\xFF\xFF\xFF\xFF')
        self.assertEqual(cm.exception.args[0], 'cannot set complex type to simple type')

    def test_fail_set_wrong_child_struct(self):
        VERSION = struct([
            (WORD, 'mn'),
            (WORD, 'mj')
        ])

        S = struct([
            (VERSION, 'v'),
            (DWORD, 'bn')
        ])
        s = S()
        dwstruct = struct([(DWORD, 'mjmn')])(b'\x00\x02\x00\x01')
        with self.assertRaises(TypeMismatch) as cm:
            s.v = dwstruct

    def test_middle_child_hex(self):
        S = struct([
            (BYTE, 'b'),
            (DWORD, 'd'),
            struct([
                (BYTE[10], 'bs'),
                (WORD, 'w')
            ], 'inn')
        ])

        bf = b'c!!!\x00\x00\x00\x001111111111bb!!!!'
        s = S(bf, target=Arch.x64)
        self.assertEqual(s.b, ord('c'))
        self.assertEqual(s.d, 0)
        self.assertEqual(bytes(s.inn.bs), b'\x31' * 10)
        self.assertEqual(s.inn.w, WORD(b'bb'))

        bf = b'c!!!\x00\x00\x00\x001111111111bb!!!!'
        s = S(bf, target=Arch.x86)
        self.assertEqual(s.b, ord('c'))
        self.assertEqual(s.d, 0)
        self.assertEqual(bytes(s.inn.bs), b'\x31' * 10)
        self.assertEqual(s.inn.w, WORD(b'bb'))

    def test_complex(self):
        S = struct([
            (BYTE, 'b'),
            (DWORD, 'd'),
            struct([
                (BYTE[10], 'bs'),
                (struct([
                    (WORD, 'w'),
                    (PVOID, 'p'),
                    (QWORD, 'q'),
                ])[3], 'ar')
            ], 'inn')
        ])

        bf = b'c!!!\x00\x00\x00\x00' + \
             b'1' * 10 + b'!' * 6 + \
             b'bb~~!!!!\x00\xFF\xFF\xFF\xFF\xFF\xFF\x0012345678' + \
             b'bb~~!!!!\x01\xFF\xFF\xFF\xFF\xFF\xFF\x01abcdefgh' + \
             b'bb~~!!!!\x02\xFF\xFF\xFF\xFF\xFF\xFF\x02ABCDEFGH'

        bf32 = b'c!!!\x00\x00\x00\x00' + \
               b'1' * 10 + b'!' * 6 + \
               b'bb~~\x00\xFF\xFF\x0012345678' + \
               b'bb~~\x01\xFF\xFF\x01abcdefgh' + \
               b'bb~~\x02\xFF\xFF\x02ABCDEFGH'

        s = S(bf, target=Arch.x64)
        self.assertEqual(s.b, ord('c'))
        self.assertEqual(s.d, 0)
        self.assertEqual(bytes(s.inn.bs), b'\x31' * 10)
        self.assertEqual(s.inn.ar[0].w, WORD(b'bb'))
        self.assertEqual(s.inn.ar[0].p, 0x00FFFFFFFFFFFF00)
        self.assertEqual(s.inn.ar[0].q, 0x3837363534333231)

        self.assertEqual(s.inn.ar[1].w, WORD(b'bb'))
        self.assertEqual(s.inn.ar[1].p, 0x01FFFFFFFFFFFF01)
        self.assertEqual(s.inn.ar[1].q, 0x6867666564636261)

        self.assertEqual(s.inn.ar[2].w, WORD(b'bb'))
        self.assertEqual(s.inn.ar[2].p, 0x02FFFFFFFFFFFF02)
        self.assertEqual(s.inn.ar[2].q, 0x4847464544434241)

        s = S(bf32, target=Arch.x86)
        self.assertEqual(s.b, ord('c'))
        self.assertEqual(s.d, 0)
        self.assertEqual(bytes(s.inn.bs), b'\x31' * 10)
        self.assertEqual(s.inn.ar[0].w, WORD(b'bb'))
        self.assertEqual(s.inn.ar[0].p, 0x00FFFF00)
        self.assertEqual(s.inn.ar[0].q, 0x3837363534333231)

        self.assertEqual(s.inn.ar[1].w, WORD(b'bb'))
        self.assertEqual(s.inn.ar[1].p, 0x01FFFF01)
        self.assertEqual(s.inn.ar[1].q, 0x6867666564636261)

        self.assertEqual(s.inn.ar[2].w, WORD(b'bb'))
        self.assertEqual(s.inn.ar[2].p, 0x02FFFF02)
        self.assertEqual(s.inn.ar[2].q, 0x4847464544434241)

    def test_init_child_array_list(self):
        S = struct([
            (BYTE[2], 'bs')
        ])

        s = S(b'12')
        self.assertEqual(s.bs[0], ord('1'))
        self.assertEqual(s.bs[1], ord('2'))
        self.assertEqual(sizeof(s), 2)
        self.assertEqual(sizeof(s.bs), 2)
        self.assertEqual(bytes(s.bs), bytes(s))
        self.assertEqual(bytes(s.bs), b'12')

        s_from_list = S({'bs': [b'1', b'2']})

        self.assertEqual(s_from_list.bs[0], ord('1'))
        self.assertEqual(s_from_list.bs[1], ord('2'))
        self.assertEqual(sizeof(s_from_list), 2)
        self.assertEqual(sizeof(s_from_list.bs), 2)
        self.assertEqual(bytes(s_from_list.bs), bytes(s))
        self.assertEqual(bytes(s_from_list.bs), b'12')

        s_from_list.bs[0] = b'q'

        self.assertEqual(s_from_list.bs[0], ord('q'))
        self.assertEqual(s_from_list.bs[1], ord('2'))
        self.assertEqual(sizeof(s_from_list), 2)
        self.assertEqual(sizeof(s_from_list.bs), 2)
        self.assertEqual(bytes(s_from_list.bs), bytes(s_from_list))
        self.assertEqual(bytes(s_from_list.bs), b'q2')

    def test_set_child_array_with_list(self):
        S = struct([
            (DWORD, 'c'),
            (BYTE[2], 'd')
        ])
        original_b = DWORD(-1) + WORD(0xccbb) + WORD(0x2121)
        s = S(original_b)
        self.assertEqual(s.c, (1 << 32) - 1)
        self.assertEqual(s.d[0], 0xbb)
        self.assertEqual(s.d[1], 0xcc)

        s.d = [1, 2]
        self.assertEqual(s.c, (1 << 32) - 1)
        self.assertEqual(s.d[0], 0x01)
        self.assertEqual(s.d[1], 0x02)
        self.assertEqual(bytes(s), DWORD(-1) + WORD(0x0201) + WORD(0x2121))

    def test_init_child_struct_with_dict(self):
        S = struct([
            (BYTE, 'c'),
            struct([
                (DWORD, 'd'),
                (BYTE, 'b')
            ], 'inner')
        ])

        buf = b'c!!!\xFF\xFF\xFF\xFFb!!!'

        s = S({'c': b'c', 'inner': {'d': -1, 'b': b'b'}})
        s_buf = S(buf)

        self.assertEqual(s.c, s_buf.c)
        self.assertEqual(s.inner.d, s_buf.inner.d)
        self.assertEqual(s.inner.b, s_buf.inner.b)

    def test_set_child_array_with_binary_string(self):
        S = struct([
            (BYTE[2], 'c'),
            (DWORD, 'd')
        ])

        s = S(b'CC!!\xFF\xFF\xFF\xFF')
        self.assertEqual(s.c[0], ord('C'))
        self.assertEqual(s.c[1], ord('C'))
        self.assertEqual(bytes(s.c), b'CC')

        s.c = b'qq'
        self.assertEqual(s.c[0], ord('q'))
        self.assertEqual(s.c[1], ord('q'))
        self.assertEqual(bytes(s.c), b'qq')
        self.assertEqual(bytes(s), b'qq!!\xFF\xFF\xFF\xFF')

    def test_set_child_struct_with_dict(self):
        S = struct([
            (BYTE, 'c'),
            struct([
                (DWORD, 'd'),
                (BYTE[4], 'b')
            ], 'inner')
        ])

        s = S(b'c!!!\xFF\xFF\xFF\xFF\x01\x02\x03\x04')

        s.inner = {'d': b'aaaa', 'b': b'bbbb'}
        self.assertEqual(s.inner.d, 0x61616161)
        self.assertEqual(bytes(s.inner.b), b'bbbb')

    def test_set_child_struct_with_binary_string(self):
        S = struct([
            (BYTE, 'c'),
            struct([
                (DWORD, 'd'),
                (BYTE[4], 'b')
            ], 'inner')
        ])

        s = S(b'c!!!\xFF\xFF\xFF\xFF\x01\x02\x03\x04')

        s.inner = b'aaaabbbb'
        self.assertEqual(s.inner.d, 0x61616161)
        self.assertEqual(bytes(s.inner.b), b'bbbb')

    def test_struct_init_stringio(self):
        try:
            from StringIO import StringIO
        except ImportError:
            from io import BytesIO as StringIO

        S = struct([
            (BYTE, 'c'),
            (PVOID, 'p'),
            (WORD, 's'),
            (DWORD, 'i')
        ])

        buffer64 = b'c!!!!!!!\x00\x00\x00\x00\x00\x00\x00\x00\x12\x12!!\xBB\xBB\xBB\xBB'
        buffer32 = b'c!!!\x00\x00\x00\x00\x12\x12!!\xBB\xBB\xBB\xBB'

        s32 = S(buffer32, target=Arch.x86)
        s32sio = S(StringIO(buffer32), target=Arch.x86)
        self.assertEqual(bytes(s32sio), bytes(s32))

        s64 = S(buffer64, target=Arch.x64)
        s64sio = S(StringIO(buffer64), target=Arch.x64)
        self.assertEqual(bytes(s64sio), bytes(s64))

    def test_struct_cannot_be_init_list(self):
        S = struct([
            (WORD[2], 'w'),
            (DWORD, 'i')
        ])

        with self.assertRaises(UnsupportedInitializationMethod) as cm:
            s = S([])
        self.assertEqual(cm.exception.args[0],
                         'struct cannot be initialized using a list or tuple; only buffer or dict')

    def test_struct_init_dict(self):
        S = struct([
            (BYTE, 'c'),
            (PVOID, 'p'),
            (WORD, 's'),
            (DWORD, 'i')
        ])

        s32 = S({'c': b'c', 'p': 0, 's': 0x1212, 'i': 0xbbbbbbbb}, target=Arch.x86)
        self.assertEqual(s32.c, ord('c'))
        self.assertEqual(s32.p, 0)
        self.assertEqual(s32.s, 0x1212)
        self.assertEqual(s32.i, 0xbbbbbbbb)

        s64 = S({'c': b'c', 'p': 0, 's': 0x1212, 'i': 0xbbbbbbbb}, target=Arch.x64)
        self.assertEqual(s64.c, ord('c'))
        self.assertEqual(s64.p, 0)
        self.assertEqual(s64.s, 0x1212)
        self.assertEqual(s64.i, 0xbbbbbbbb)

    def test_struct_basic(self):
        A = struct([
            (BYTE, 'c'),
            (PVOID, 'p'),
            (WORD, 's'),
            (DWORD, 'i')
        ])

        buffer64 = b'c!!!!!!!\x00\x00\x00\x00\x00\x00\x00\x00\x12\x12!!\xBB\xBB\xBB\xBB'
        buffer32 = b'c!!!\x00\x00\x00\x00\x12\x12!!\xBB\xBB\xBB\xBB'

        self.assertEqual(A.__align__, PVOID.__align__)
        self.assertEqual(A.__size__, (len(buffer32), len(buffer64)))
        self.assertEqual(A.__pad__, (0, 0))
        self.assertEqual(A.__pack__, 0)
        self.assertEqual(A.__machdep__, True)
        self.assertEqual(A.__accessor__, '')
        self.assertEqual(A.__offsets__, [
            (0, 0),
            (4, 8),
            (8, 16),
            (12, 20)
        ])

        a64 = A(buffer64, target=Arch.x64)
        self.assertEqual(a64.c, ord('c'))
        self.assertEqual(a64.p, 0)
        self.assertEqual(a64.s, 0x1212)
        self.assertEqual(a64.i, 0xbbbbbbbb)

        a32 = A(buffer32, target=Arch.x86)
        self.assertEqual(a32.c, ord('c'))
        self.assertEqual(a32.p, 0)
        self.assertEqual(a32.s, 0x1212)
        self.assertEqual(a32.i, 0xbbbbbbbb)

    def test_struct_nested_diff_pack(self):
        with pragma.pack(4):
            E = struct([
                (WORD, 's'),
                (PVOID, 'p')
            ])

        e_buffer32 = b'\x12\x12!!\x00\x00\x00\x00'
        e_buffer64 = e_buffer32 + b'\x00\x00\x00\x00'

        self.assertEqual(E.__align__, (4, 4))
        self.assertEqual(E.__size__, (len(e_buffer32), len(e_buffer64)))
        self.assertEqual(E.__pad__, (0, 0))
        self.assertEqual(E.__pack__, 4)
        self.assertEqual(E.__machdep__, True)
        self.assertEqual(E.__accessor__, '')
        self.assertEqual(E.__offsets__, [
            (0, 0),
            (4, 4)
        ])

        e64 = E(e_buffer64, target=Arch.x64)
        self.assertEqual(e64.s, 0x1212)
        self.assertEqual(e64.p, 0)

        e32 = E(e_buffer32, target=Arch.x86)
        self.assertEqual(e32.s, 0x1212)
        self.assertEqual(e32.p, 0)

        f_buffer32 = b'c!!!' + e_buffer32
        f_buffer64 = b'c!!!' + e_buffer64

        F = struct([
            (BYTE, 'c'),
            (E, 'e')
        ])

        self.assertEqual(F.__align__, F.e.__align__)
        self.assertEqual(F.__size__, (len(f_buffer32), len(f_buffer64)))
        self.assertEqual(F.__pad__, (0, 0))
        self.assertEqual(F.__pack__, 0)
        self.assertEqual(F.__machdep__, True)
        self.assertEqual(F.__accessor__, '')
        self.assertEqual(F.__offsets__, [
            (0, 0),
            (4, 4)
        ])

        f64 = F(f_buffer64, target=Arch.x64)
        self.assertEqual(f64.c, ord('c'))
        self.assertEqual(f64.e.s, 0x1212)
        self.assertEqual(f64.e.p, 0)

        f32 = F(f_buffer32, target=Arch.x86)
        self.assertEqual(f32.c, ord('c'))
        self.assertEqual(f32.e.s, 0x1212)
        self.assertEqual(f32.e.p, 0)

    def test_struct_with_padding(self):
        G = struct([
            (WORD, 's'),
            (PVOID, 'p'),
            (BYTE, 'c')
        ])

        g_buffer32 = b'\x12\x12!!\x00\x00\x00\x00c!!!'
        g_buffer64 = b'\x12\x12!!!!!!\x00\x00\x00\x00\x00\x00\x00\x00c!!!!!!!'

        self.assertEqual(G.__align__, PVOID.__align__)
        self.assertEqual(G.__size__, (len(g_buffer32), len(g_buffer64)))
        self.assertEqual(G.__pad__, (3, 7))
        self.assertEqual(G.__pack__, 0)
        self.assertEqual(G.__machdep__, True)
        self.assertEqual(G.__accessor__, '')
        self.assertEqual(G.__offsets__, [
            (0, 0),
            (4, 8),
            (8, 16)
        ])

        g32 = G(g_buffer32, target=Arch.x86)
        self.assertEqual(g32.s, 0x1212)
        self.assertEqual(g32.p, 0)
        self.assertEqual(g32.c, ord('c'))

        g64 = G(g_buffer64, target=Arch.x64)
        self.assertEqual(g64.s, 0x1212)
        self.assertEqual(g64.p, 0)
        self.assertEqual(g64.c, ord('c'))

    def test_struct_basic_update(self):
        S = struct([
            (WORD, 's'),
            (PVOID, 'p'),
            (BYTE, 'c')
        ])

        s32 = S(b'\x12\x12!!\x00\x00\x00\x00c!!!', target=Arch.x86)
        self.assertEqual(s32.s, 0x1212)
        self.assertEqual(s32.p, 0)
        self.assertEqual(s32.c, ord('c'))
        self.assertEqual(bytes(s32), b'\x12\x12!!\x00\x00\x00\x00c!!!')
        s32.s = 0x3333
        s32.p = 0xffffffff
        self.assertEqual(s32.s, 0x3333)
        self.assertEqual(s32.p, 0xffffffff)
        self.assertEqual(s32.c, ord('c'))
        self.assertEqual(bytes(s32), b'\x33\x33!!\xFF\xFF\xFF\xFFc!!!')

        s64 = S(b'\x12\x12!!!!!!\x00\x00\x00\x00\x00\x00\x00\x00c!!!!!!!', target=Arch.x64)
        self.assertEqual(s64.s, 0x1212)
        self.assertEqual(s64.p, 0)
        self.assertEqual(s64.c, ord('c'))

        s64.s = 0x3333
        s64.p = 0xffffffffffffffff
        self.assertEqual(s64.s, 0x3333)
        self.assertEqual(s64.p, 0xffffffffffffffff)
        self.assertEqual(s64.c, ord('c'))
        self.assertEqual(bytes(s64), b'\x33\x33!!!!!!\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFFc!!!!!!!')

    def test_struct_type_sizeof(self):
        S = struct([
            (WORD, 's'),
            (PVOID, 'p'),
            (BYTE, 'c')
        ])
        s32 = S(b'\x12\x12!!\x00\x00\x00\x00c!!!', target=Arch.x86)
        s64 = S(b'\x12\x12!!!!!!\x00\x00\x00\x00\x00\x00\x00\x00c!!!!!!!', target=Arch.x64)
        self.assertEqual(sizeof(S, Arch.x86), sizeof(s32))
        self.assertEqual(sizeof(S, Arch.x64), sizeof(s64))

    def test_struct_type_sizeof_error(self):
        S = struct([
            (WORD, 's'),
            (PVOID, 'p'),
            (BYTE, 'c')
        ])

        with self.assertRaises(ArchDependentType) as cm:
            bad = sizeof(S)

    def test_struct_offsetof(self):
        S = struct([
            (WORD, 's'),
            (PVOID, 'p'),
            (BYTE, 'c')
        ])

        s32 = S(b'\x12\x12!!\x00\x00\x00\x00c!!!', target=Arch.x86)
        s64 = S(b'\x12\x12!!!!!!\x00\x00\x00\x00\x00\x00\x00\x00c!!!!!!!', target=Arch.x64)

        self.assertEqual(offsetof('p', s32), 4)
        self.assertEqual(offsetof('p', s64), 8)

    def test_struct_type_offsetof(self):
        S = struct([
            (WORD, 's'),
            (PVOID, 'p'),
            (BYTE, 'c')
        ])

        s32 = S(b'\x12\x12!!\x00\x00\x00\x00c!!!', target=Arch.x86)
        s64 = S(b'\x12\x12!!!!!!\x00\x00\x00\x00\x00\x00\x00\x00c!!!!!!!', target=Arch.x64)

        self.assertEqual(offsetof('p', S, target_arch=Arch.x86), 4)
        self.assertEqual(offsetof('p', S, target_arch=Arch.x64), 8)

    def test_struct_type_offsetof_error(self):
        S = struct([
            (WORD, 's'),
            (PVOID, 'p'),
            (BYTE, 'c')
        ])

        with self.assertRaises(ArchDependentType) as cm:
            bad = offsetof('p', S)

    def test_struct_bad_init_def(self):
        with self.assertRaises(UnsupportedInitializationMethod) as cm:
            S = struct([])
        self.assertEqual(cm.exception.args[0], 'requires field definitions')

        with self.assertRaises(UnsupportedInitializationMethod) as cm:
            S = struct([list])
        self.assertEqual(cm.exception.args[0], 'input must be simple or complex type-definition')

        with self.assertRaises(UnsupportedInitializationMethod) as cm:
            S = struct([1])
        self.assertEqual(cm.exception.args[0], 'unsupported input for type-member tuple')
