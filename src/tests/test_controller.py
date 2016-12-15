try:
    import unittest2 as unittest
except ImportError:
    import unittest

from GDGUkraine.lib.testing import TestCase


class RootTest(TestCase):

    # TODO: complete this test
    @unittest.mock.patch('GDGUkraine.api.get_all_gdg_places',
                         new=lambda sess, filtered: [])
    def test_index(self):
        self.getPage('/')
        self.assertStatus(200)
