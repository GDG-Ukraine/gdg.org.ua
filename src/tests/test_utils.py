import cherrypy
from blueberrypy.testing import ControllerTestCase

from GDGUkraine.utils import url_for, base_url


class UtilTest(ControllerTestCase):
    """Test for Utils"""
    urls_testset = (
        {'inp': {'handler': 'Controller.Root', 'type_': 'class-based'},
         'res': ''},
        {'inp': {'handler': 'Controller.Root.auth.google',
                 'type_': 'class-based'},
         'res': 'auth/google'},
        {'inp': {'handler': 'Controller.Root.auth.logout',
                 'type_': 'class-based'},
         'res': 'auth/logout'},
        {'inp': {'handler': 'Controller.Root.auth.logout',
                 'type_': 'class-based',
                 'url_args': ['http://test.ua/xx']},
         'res': 'auth/logout/http%3A%2F%2Ftest.ua%2Fxx'},

        {'inp': {'handler': 'list_participants',
                 'type_': 'routes'},
         'res': 'api/participants'},
        {'inp': {'handler': 'add_participant',
                 'type_': 'routes'},
         'res': 'api/participants'},
        {'inp': {'handler': 'export_event_participants',
                 'type_': 'routes', 'url_params': {'id': 5}},
         'res': 'api/events/5/export_participants'},

        {'inp': {'handler': 'event_register', 'url_params': {'id': 7},
                 'type_': 'routes'},
         'res': 'events/7/register'},

        {'inp': {'handler': 'abuse',
                 'type_': 'cherrypy'},
         'res': 'abuse'},
        {'inp': {'handler': 'authors',
                 'type_': 'cherrypy'},
         'res': 'authors'},

        {'inp': {'handler': 'img/gdg.png',
                 'type_': 'static'},
         'res': 'img/gdg.png'},
    )

    urls_exc_testset = (
        {'inp': {'handler': 'Controller.Root.auth.logout',
                 'type_': 'class-based',
                 'url_args': ['sdf', 'sdf2'],
                 'url_params': {'4': 1, 'asdf': '1'}},
         'res': TypeError},
    )

    def setUp(self):
        cherrypy.config.update({'cherrypy.engine.url_for.on': True})

    def test_url_for(self):
        for test_url in self.urls_testset:
            self.assertEqual(url_for(
                **test_url['inp']), '/'.join([base_url(), test_url['res']]))

        for test_url in self.urls_exc_testset:
            with self.assertRaises(test_url['res']):
                url_for(**test_url['inp'])
