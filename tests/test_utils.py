import random
import sys
import unittest

import runai.utils

def foo():
    return 42

class Object:
    def foo(self):
        return 42

class Hook(runai.utils.Hook):
    def __init__(self, module):
        super(Hook, self).__init__(module, 'foo')

    def __hook__(self):
        return 217

class TestHook(unittest.TestCase):
    def test_module_scope(self):
        assert foo() == 42

        with Hook(sys.modules[__name__]):
            assert foo() == 217

        assert foo() == 42

    def test_module_manual(self):
        hook = Hook(sys.modules[__name__])
        assert foo() == 42

        hook.enable()
        assert foo() == 217

        hook.disable()
        assert foo() == 42

    def test_object(self):
        o = Object()
        
        assert o.foo() == 42

        with Hook(o):
            assert o.foo() == 217

        assert o.foo() == 42

    def test_object_manual(self):
        o = Object()
        hook = Hook(o)
        assert o.foo() == 42
        
        hook.enable()
        assert o.foo() == 217
        
        hook.disable()
        assert o.foo() == 42

    def test_recursion(self):
        class Module:
            @staticmethod
            def foo(x):
                return x + 10
        
        def hook(x):
            return Module.foo(x) + 1
        
        for recursion in [True, False]:
            with runai.utils.Hook(Module, 'foo', hook, recursion=recursion):
                if recursion:
                    with self.assertRaises(RecursionError):
                        Module.foo(0)
                else:
                    assert Module.foo(0) == 11

class TestRandom(unittest.TestCase):
    def test_string(self):
        for _ in range(50):
            length = runai.utils.random.number(5, 10)
            a = runai.utils.random.string(length=length)
            b = runai.utils.random.string(length=length)

            assert len(a) == length
            assert len(b) == length

            assert a != b

    def test_strings(self):
        count = runai.utils.random.number(5, 10)
        
        assert len(runai.utils.random.strings(count=count)) == count

if __name__ == '__main__':
    unittest.main()
