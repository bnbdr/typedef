from base import *


class Pragma(TypedefTestCase):
    def test_empty_pack_remains_infer(self):
        pragma.pack._stack = []
        self.assertEqual(pragma.pack.pop(), pragma.pack.Current)
        self.assertEqual(pragma.pack._default, pragma.pack.Current)

    def test_valid_pack_values(self):
        for pack_value in [pragma.pack.Infer, 1, 2, 4, 8, 16]:
            pragma.pack.push(pack_value)
            self.assertEqual(pack_value, pragma.pack.Current)
            pragma.pack.pop()

    def test_pack_without_value(self):
        with self.assertRaises(PragmaValueMissing) as cm:
            with pragma.pack:
                pass

        self.assertEqual(cm.exception.args[0], 'missing pragma value')

    def test_bad_pack_values(self):
        for pack_value in [3, 5, 'a', '2', dict(), list]:
            with self.assertRaises(UnsupportedPragmaPack) as cm:
                pragma.pack.push(pack_value)
        self.assertEqual(cm.exception.args[0], 'unsupported pack value')
