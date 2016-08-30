from GDGUkraine.lib.testing import TestCase


class RootTest(TestCase):

    def test_index(self):
        self.getPage('/')
        self.assertStatus(200)
