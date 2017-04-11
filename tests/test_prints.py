from base import *


class Print(TypedefTestCase):
    def test_repr(self):
        d = DWORD[2]()
        self.assertEqual(repr(d), '00 00 00 00 00 00 00 00')

    def test_bytes_gives_buffer(self):
        a = BYTE[6]()
        self.assertEqual(bytes(a), b'\x00'*6)