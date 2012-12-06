from blueberrypy.testing import ControllerTestCase

class RootTest(ControllerTestCase):

    def test_index(self):
        self.getPage("/")
        self.assertStatus(200)