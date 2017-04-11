import unittest
import warnings
from sys import version_info
from os import path, remove
import gc
from typedef import *
from typedef.errors import *  # for when tests import this module

py_v = version_info


def print_references(l, base_path):
    import objgraph
    objgraph.show_backrefs(l, filename=base_path + '.backrefs.png')
    objgraph.show_refs(l, filename=base_path + '.refs.png')


class TypedefTestCase(unittest.TestCase):
    def setUp(self):
        print ('\r > ' + self.id())
        pragma.pack.push(pragma.pack.Infer)
        self.test_base_path = path.join(path.dirname(path.realpath(__file__)), self.id().split('.')[-1])
        self.test_file_path = self.test_base_path + '.bin'

        if path.exists(self.test_file_path):
            remove(self.test_file_path)

    def tearDown(self):

        if path.exists(self.test_file_path):
            remove(self.test_file_path)

        gc.collect()
        if gc.garbage:
            print_references(self.test_base_path)
            self.assertEqual(gc.garbage, [], 'reference leak detected, for objgraph output look at `{}`'.format(
                self.test_base_path))

        pragma.pack.pop()
