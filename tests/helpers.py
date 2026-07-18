import sys
import unittest

VERBOSE = "-v" in sys.argv or "--verbose" in sys.argv


def vprint(*args, **kwargs):
    if VERBOSE:
        print(*args, flush=True, **kwargs)


class VerboseTestCase(unittest.TestCase):
    def setUp(self):
        vprint()
