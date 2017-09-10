from base import *


class Sign(TypedefTestCase):
    def test_operator(self):
        self.assertIs(DWORD, abs(DWORD))
        self.assertIsNot(DWORD, ~DWORD)
        self.assertIs(DWORD, abs(~DWORD))

    def test_parse(self):
        max_uint32 = 2 ** 32 - 1
        buffer = b'\xff\xff\xff\xff'

        self.assertEqual((~DWORD)(buffer), -1)
        self.assertEqual(DWORD(buffer), max_uint32)

    def test_to_buffer(self):
        self.assertEqual(BYTE(-1), b'\xFF')
        self.assertEqual(WORD(-1), b'\xFF\xFF')
        self.assertEqual(DWORD(-1), b'\xFF\xFF\xFF\xFF')
        self.assertEqual(QWORD(-1), b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF')

    def test_from_buffer(self):
        max_uint8 = 2 ** 8 - 1
        max_uint16 = 2 ** 16 - 1
        max_uint32 = 2 ** 32 - 1
        max_uint64 = 2 ** 64 - 1

        self.assertEqual((~BYTE)(b'\xFF'), -1)
        self.assertEqual((~WORD)(b'\xFF\xFF'), -1)
        self.assertEqual((~DWORD)(b'\xFF\xFF\xFF\xFF'), -1)
        self.assertEqual((~QWORD)(b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF'), -1)

        self.assertEqual(BYTE(b'\xFF'), max_uint8)
        self.assertEqual(WORD(b'\xFF\xFF'), max_uint16)
        self.assertEqual(DWORD(b'\xFF\xFF\xFF\xFF'), max_uint32)
        self.assertEqual(QWORD(b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF'), max_uint64)


class Endian(TypedefTestCase):
    def test_operator(self):
        self.assertIs(DWORD, -DWORD)
        self.assertIs(+DWORD, +DWORD)
        self.assertIsNot(DWORD, +DWORD)

    def test_parse(self):
        buffer = b'\x01\x00\x00\x00'

        self.assertEqual((+DWORD)(buffer), 0x01000000)
        self.assertEqual((-DWORD)(buffer), 0x00000001)


class Union(TypedefTestCase):
    def test_signed_unsigned_big_little_accessors(self):
        U = union([
            (DWORD, 'unsignedLittle'),
            (~DWORD, 'signedLittle'),
            (+DWORD, 'unsignedBig'),
            (+~DWORD, 'signedBig')
        ])
        import struct as pystruct

        b = b'\xb0\x02\x03\x04'
        u = U(b)
        self.assertEqual(u.unsignedLittle, pystruct.unpack('<I', b)[0])
        self.assertEqual(u.signedLittle, pystruct.unpack('<i', b)[0])
        self.assertEqual(u.unsignedBig, pystruct.unpack('>I', b)[0])
        self.assertEqual(u.signedBig, pystruct.unpack('>i', b)[0])


class Size(TypedefTestCase):
    def test_sizeof(self):
        self.assertEqual(sizeof(BYTE), 1)
        self.assertEqual(sizeof(WORD), 2)
        self.assertEqual(sizeof(DWORD), 4)
        self.assertEqual(sizeof(QWORD), 8)

        self.assertEqual(sizeof(PVOID, Arch.x86), 4)
        self.assertEqual(sizeof(PVOID, Arch.x64), 8)
