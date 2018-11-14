import unittest
from test import test_support

class ExposedMethodStackRecursion(unittest.TestCase):

    def test_java_str_repr_overrides(self):
        """Py2kbuffer overrides __str__ and __repr__ directly in a PyObject subclass."""

        # buffer interface translates to utf16-be on unicode input.
        b=buffer(u'asdf')
        self.assertEqual(str(b),b'\x00a\x00s\x00d\x00f')
        # __str__ is exposed from Py2kBuffer
        self.assertEqual(str(b), b.__str__())
        # __repr__ is customized
        self.assertRegexpMatches(repr(b),
                                 r'<read-only buffer for 0x[\da-f]+, size -1, offset 0 at 0x[\da-f]+>')
        # __repr__ is exposed
        self.assertEqual(b.__repr__(),repr(b))

    def test_derived_recursion(self):
        """when PyObject exposes a method by it's actual name, the exposed facade delegates through
        "  subclasses in PyObjectDerived and other ..Derived.  This fixes the above test, but opens
        "  up a recursion issue.
        """

        class F(object):
            """Doesn't trigger recursion when exposed method is overriden."""
            def __repr__(self): return "myrepr"
            def __str__(self): return "mystr"

        class E(object):
            """This never passes through to super.__str__ or super.__repr__ in PyObjectDerived.java"""
            pass

        self.assertEqual(F().__str__(), "mystr")
        self.assertEqual(str(F()), "mystr")
        self.assertEqual(F().__repr__(), "myrepr")
        self.assertEqual(repr(F()), "myrepr")

        # Raises Java StackOverflowError
        try:
            E().__str__()
            E().__repr__()
            str(E())
            repr(E())
        except RuntimeError as e:
            self.fail("Exposed method recursion through derrived: %s" % (e))

def test_main():
    test_support.run_unittest(__name__)

if __name__ == "__main__":
    test_main()