from base import *


class Union(TypedefTestCase):
    def test_union_cannot_be_init_dict(self):
        U = union([
            (WORD[2], 'w'),
            (DWORD, 'i')
        ])

        with self.assertRaises(UnsupportedInitializationMethod) as cm:
            u = U({})
        self.assertEqual(cm.exception.args[0], 'union cannot be initialized using a dict/list/tuple; only buffer')

    def test_union_with_nameless_struct(self):
        U = union([
            struct([
                (WORD, 'mn'),
                (WORD, 'mj'),
            ]),
            (DWORD, 'build')
        ])

        self.assertEqual(U.__size__, DWORD.__size__)
        self.assertEqual(U.__offsets__, [(0, 0), (2, 2), (0, 0)])
        u = U(b'aabb')
        self.assertEqual(u.mn, WORD(b'aa'))
        self.assertEqual(u.mj, WORD(b'bb'))
        self.assertEqual(u.build, DWORD(b'aabb'))

    def test_union_with_struct(self):
        U = union([
            struct([
                (WORD, 'mn'),
                (WORD, 'mj'),
            ], 'version'),
            (DWORD, 'build')
        ])

        self.assertEqual(U.__align__, DWORD.__align__)
        self.assertEqual(U.__size__, U.version.__size__)
        self.assertEqual(U.__pad__, (0, 0))
        self.assertEqual(U.__pack__, 0)
        self.assertEqual(U.__machdep__, False)
        self.assertEqual(U.__accessor__, '')
        self.assertEqual(U.__offsets__, [
            (0, 0),
            (0, 0)
        ])

        u = U(b'\x01\00\x02\x00')
        self.assertEqual(u.version.mn, 1)
        self.assertEqual(u.version.mj, 2)
        self.assertEqual(u.build, 0x00020001)

    def test_union_with_array(self):
        U = union([
            (DWORD, 'dw'),
            (BYTE[4], 'bytes')
        ])

        self.assertEqual(U.__align__, DWORD.__align__)
        self.assertEqual(U.__size__, (4, 4))
        self.assertEqual(U.__pad__, (0, 0))
        self.assertEqual(U.__pack__, 0)
        self.assertEqual(U.__machdep__, False)
        self.assertEqual(U.__accessor__, '')
        self.assertEqual(U.__offsets__, [
            (0, 0),
            (0, 0)
        ])

        u = U(b'\x00\x01\x02\x03')
        self.assertEqual(u.bytes[0], 0x00)
        self.assertEqual(u.bytes[1], 0x01)
        self.assertEqual(u.bytes[2], 0x02)
        self.assertEqual(u.bytes[3], 0x03)

        self.assertEqual(u.dw & 0x000000FF, u.bytes[0])
        self.assertEqual(u.dw & 0x0000FF00, u.bytes[1] << 8)
        self.assertEqual(u.dw & 0x00FF0000, u.bytes[2] << 16)
        self.assertEqual(u.dw & 0xFF000000, u.bytes[3] << 24)

    def test_union_basic(self):
        U = union([
            (BYTE, 'c'),
            (WORD, 's'),
            (DWORD, 'i'),
            (PVOID, 'p')
        ])

        u_buffer32 = b'\x11\x22\x33\x44'
        u_buffer64 = u_buffer32 + b'\x00\x00\x00\xFF'

        self.assertEqual(U.__align__, PVOID.__align__)
        self.assertEqual(U.__size__, (len(u_buffer32), len(u_buffer64)))
        self.assertEqual(U.__pad__, (0, 0))
        self.assertEqual(U.__pack__, 0)
        self.assertEqual(U.__machdep__, True)
        self.assertEqual(U.__accessor__, '')
        self.assertEqual(U.__offsets__, [
            (0, 0),
            (0, 0),
            (0, 0),
            (0, 0)
        ])

        u64 = U(u_buffer64, target=Arch.x64)
        self.assertEqual(u64.c, 0x11)
        self.assertEqual(u64.s, 0x2211)
        self.assertEqual(u64.i, 0x44332211)
        self.assertEqual(u64.p, 0xFF00000044332211)

        u32 = U(u_buffer32, target=Arch.x86)
        self.assertEqual(u32.c, 0x11)
        self.assertEqual(u32.s, 0x2211)
        self.assertEqual(u32.i, 0x44332211)
        self.assertEqual(u32.p, 0x44332211)
