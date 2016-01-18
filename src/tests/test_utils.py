from blueberrypy.testing import ControllerTestCase

from GDGUkraine.utils import build_url_map, url_for, base_url


class UtilTest(ControllerTestCase):
    """Test for Utils"""
    urls_testset = (
        {'inp': {'handler': 'Controller.Root', 'type_': 'class-based'},
         'res': '/'.join([base_url, '/'])},
        {'inp': {'handler': 'Controller.Root.auth.google',
                 'type_': 'class-based'},
         'res': '/'.join([base_url, '/auth/google'])},
        {'inp': {'handler': 'Controller.Root.auth.logout',
                 'type_': 'class-based'},
         'res': '/'.join([base_url, '/auth/logout'])},
        {'inp': {'handler': 'Controller.Root.auth.logout',
                 'type_': 'class-based',
                 'url_args': ['http://test.ua/xx']},
         'res': '/'.join([base_url,
                          '/auth/logout/http%3A%2F%2Ftest.ua%2Fxx'])},
    )

    urls_exc_testset = (
        {'inp': {'handler': 'Controller.Root.auth.logout',
                 'type_': 'class-based',
                 'url_args': ['sdf', 'sdf2'],
                 'url_params': {'4': 1, 'asdf': '1'}},
         'res': TypeError},
    )

    def setUp(self):
        build_url_map(force=True)

    def test_url_for(self):
        for test_url in self.urls_testset:
            self.assertEqual(url_for(**test_url['inp']), test_url['res'])

        for test_url in self.urls_exc_testset:
            with self.assertRaises(test_url['res']):
                url_for(**test_url['inp'])
