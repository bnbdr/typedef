from base import *


class InitPassthrough(TypedefTestCase):
    @unittest.skipIf(py_v.major > 2,
                     "not supported in this python version")
    def test_init_passthrough_bad_cstringio_permissions(self):
        from cStringIO import StringIO

        S = struct([
            (DWORD, 'd'),
            (BYTE[4], 'b')
        ])

        readonly_sio = StringIO('\x00\x00\x00\x00\xAA\xBB\xCC\xDD')
        with self.assertRaises(AttributeError) as cm:
            s = S(readonly_sio, mode=F_SYNC)

        self.assertEqual(cm.exception.message, "'cStringIO.StringI' object has no attribute 'write'")

    def test_init_passthrough_bad_fd_permissions(self):
        S = struct([
            (DWORD, 'd'),
            (BYTE[4], 'b')
        ])
        with warnings.catch_warnings(record=True):  # to ignore warning on unclosed file
            open(self.test_file_path, 'wb').write(b'\x00\x00\x00\x00\xAA\xBB\xCC\xDD')

        with self.assertRaises(IOError) as cm:
            f = open(self.test_file_path, 'rb')
            s = S(f, mode=F_SYNC)
        f.close()  # to shutup warning; never closes since its not used by struct S
        self.assertTrue(cm.exception.args[0] in ['File not open for writing', 'write'])

    def test_init_passthrough_sync(self):
        S = struct([
            (DWORD, 'd'),
            (BYTE[4], 'b')
        ])

        with warnings.catch_warnings(record=True):  # to ignore warning on unclosed file
            open(self.test_file_path, 'wb').write(b'\x00\x00\x00\x00\xAA\xBB\xCC\xDD')
        s = S(open(self.test_file_path, 'r+b'), mode=F_SYNC)
        self.assertEqual(s.d, 0)
        self.assertEqual(s.b[0], 0xAA)
        self.assertEqual(s.b[1], 0xBB)
        self.assertEqual(s.b[2], 0xCC)
        self.assertEqual(s.b[3], 0xDD)
        s.d = -1
        s.b[0] = 1
        s.b[1] = 2
        s.b[2] = 3
        s.b[3] = 4

        with warnings.catch_warnings(record=True):  # to ignore warning on unclosed file
            data = open(self.test_file_path, 'rb').read()
        self.assertEqual(data, bytes(s))
        # s.__buffer__.close()
