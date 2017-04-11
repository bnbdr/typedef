from base import *


class Array(TypedefTestCase):
    def test_set_child_struct_with_binary_string(self):
        S = struct([
            (DWORD, 'd'),
            (WORD, 'w')
        ])

        a = S[2](b'\x00\x00\x00\x00\xBB\xBB!!aaaabb!!')
        self.assertEqual(a[0].d, 0)
        self.assertEqual(a[0].w, 0xbbbb)
        a[0] = b'\xBB\xBB\x00\x00\x00\x00!!'
        self.assertEqual(a[0].d, 0xbbbb)
        self.assertEqual(a[0].w, 0)

    def test_padding_in_struct(self):
        S = struct([
            (BYTE[3], 'ss'),
            (PVOID, 'p'),
            (BYTE, 'c')
        ])

        self.assertEqual(S.__align__, PVOID.__align__)
        self.assertEqual(S.__size__, (3 + 1 + 4 + 1 + 3, 3 + 5 + 8 + 1 + 7))
        self.assertEqual(S.__pad__, (3, 7))
        self.assertEqual(S.__pack__, 0)
        self.assertEqual(S.__machdep__, True)
        self.assertEqual(S.__accessor__, '')
        self.assertEqual(S.__offsets__, [
            (0, 0),
            (4, 8),
            (8, 16)
        ])

        self.assertEqual(len(S.ss), 3)
        self.assertEqual(S.ss.__align__, (1, 1))
        self.assertEqual(S.ss.__pad__, (0, 0))
        self.assertEqual(S.ss.__size__, (3, 3))
        self.assertEqual(S.ss.__machdep__, False)

    def test_padding_in_child_struct(self):
        S = struct([
            (WORD, 's'),
            (PVOID, 'p'),
            (BYTE, 'c')
        ])
        self.assertEqual(S.__pad__, (3, 7))

        a32 = S[2](b'\x12\x12!!\x00\x00\x00\x00c!!!' * 2, target=Arch.x86)
        self.assertEqual(a32[0].s, 0x1212)
        self.assertEqual(a32[0].p, 0)
        self.assertEqual(a32[0].c, ord('c'))
        self.assertEqual(bytes(a32[0]), b'\x12\x12!!\x00\x00\x00\x00c!!!')
        self.assertEqual(a32[1].s, 0x1212)
        self.assertEqual(a32[1].p, 0)
        self.assertEqual(a32[1].c, ord('c'))
        self.assertEqual(bytes(a32[1]), b'\x12\x12!!\x00\x00\x00\x00c!!!')

        a64 = S[2](b'\x12\x12!!!!!!\x00\x00\x00\x00\x00\x00\x00\x00c!!!!!!!' * 2, target=Arch.x64)
        self.assertEqual(a64[0].s, 0x1212)
        self.assertEqual(a64[0].p, 0)
        self.assertEqual(a64[0].c, ord('c'))
        self.assertEqual(bytes(a64[0]), b'\x12\x12!!!!!!\x00\x00\x00\x00\x00\x00\x00\x00c!!!!!!!')
        self.assertEqual(a64[1].s, 0x1212)
        self.assertEqual(a64[1].p, 0)
        self.assertEqual(a64[1].c, ord('c'))
        self.assertEqual(bytes(a64[1]), b'\x12\x12!!!!!!\x00\x00\x00\x00\x00\x00\x00\x00c!!!!!!!')

    def test_to_buffer(self):
        dwords = DWORD[4]()
        dw_buffer = b'\x01\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00\x04\x00\x00\x00'

        dwords[0] = 0x01
        dwords[1] = 0x02
        dwords[2] = 0x03
        dwords[3] = 0x04

        self.assertEqual(dw_buffer, bytes(dwords))

    def test_init_from_list(self):
        ds = DWORD[3]([1, 2, 3])
        self.assertEqual(ds[0], 1)
        self.assertEqual(ds[1], 2)
        self.assertEqual(ds[2], 3)

        dw_buffer = b'\x01\x00\x00\x00' + b'\x02\x00\x00\x00' + b'\x03\x00\x00\x00'
        self.assertEqual(dw_buffer, bytes(ds))

    def test_length(self):
        a = array(DWORD, 3)
        b = DWORD[3]

        # assert b is a
        self.assertEqual(len(a), 3)
        self.assertEqual(len(b), 3)

    def test_no_nested_arrays(self):
        with self.assertRaises(TypeError) as cm:
            four_dws = (DWORD[2])[2]
        self.assertEqual(cm.exception.args[0],
                         "'ArrayMeta' object does not support indexing")  # cm.exception doesnt have message in py3

    def test_nested_arrays_bypass(self):
        two_dws_s = struct([(DWORD[2], 'arr')])

        fdws = two_dws_s[2](DWORD(0x11) + DWORD(0x12) + DWORD(0x21) + DWORD(0x22))
        self.assertEqual(fdws[0].arr[0], 0x11)
        self.assertEqual(fdws[0].arr[1], 0x12)
        self.assertEqual(fdws[1].arr[0], 0x21)
        self.assertEqual(fdws[1].arr[1], 0x22)

    def test_array_basic_update(self):
        A = DWORD[2]

        self.assertEqual(len(A), 2)
        buf = b'aaaabbbb'
        a = A(buf)
        self.assertEqual(a[0], 0x61616161)
        self.assertEqual(a[1], 0x62626262)
        self.assertEqual(bytes(a), buf)
        a[0] = 0x63636363

        self.assertEqual(a[0], 0x63636363)
        self.assertEqual(a[1], 0x62626262)
        self.assertEqual(bytes(a), b'cccc' + buf[4:])

    def test_array_basic_infer(self):
        A = DWORD[2]

        self.assertEqual(A.__align__, DWORD.__align__)
        self.assertEqual(A.__size__, (2 * 4, 2 * 4))
        self.assertEqual(A.__pad__, (0, 0))
        self.assertEqual(A.__pack__, 0)
        self.assertEqual(A.__machdep__, False)
        self.assertEqual(A.__accessor__, '')
        self.assertEqual(A.__offsets__, [
            (0, 0),
            (4, 4)
        ])

        buf = b'aaaabbbb'
        a = A(buf)

        self.assertEqual(a[0], 0x61616161)
        self.assertEqual(a[1], 0x62626262)
        self.assertEqual(sizeof(a), len(buf))

        bbuf = b'abcdefgh'
        B = BYTE[len(bbuf)]

        self.assertEqual(B.__align__, BYTE.__align__)
        self.assertEqual(B.__size__, (len(bbuf), len(bbuf)))
        self.assertEqual(B.__pad__, (0, 0))
        self.assertEqual(B.__pack__, 0)
        self.assertEqual(B.__machdep__, False)
        self.assertEqual(A.__accessor__, '')
        self.assertEqual(B.__offsets__, [
            (0, 0),
            (1, 1),
            (2, 2),
            (3, 3),
            (4, 4),
            (5, 5),
            (6, 6),
            (7, 7),
        ])

        b = B(bbuf)
        self.assertEqual(b[0], ord('a'))
        self.assertEqual(b[1], ord('b'))
        self.assertEqual(b[2], ord('c'))
        self.assertEqual(b[3], ord('d'))
        self.assertEqual(b[4], ord('e'))
        self.assertEqual(b[5], ord('f'))
        self.assertEqual(b[6], ord('g'))
        self.assertEqual(b[7], ord('h'))

        # gc.collect()
        # print gc.get_referrers(b)
