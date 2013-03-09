import unittest
from tests.test_collection import CollectionTestCase

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(CollectionTestCase)
