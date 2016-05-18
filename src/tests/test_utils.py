try:
    import unittest2 as unittest
except ImportError:
    import unittest

import cherrypy
from blueberrypy.testing import ControllerTestCase

from openpyxl import load_workbook

from GDGUkraine.lib.utils.table_exporter import TableExporter
from GDGUkraine.lib.utils.url import base_url, url_for
from GDGUkraine.lib.utils.vcard import pad


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


class TableExporterTest(unittest.TestCase):
    testset = [
        {"username": "sviat", "distro": "gentoo", "tv_show": "X-Files"},
        {"username": "sashko", "distro": "gentoo", "tv_show": "MLP"},
        {"username": "vlad", "distro": "windows", "tv_show": None},
    ]

    getters = [
        ('User name', lambda x: x.get('username', '')),
        ('OS', lambda x: x.get('distro', '')),
    ]

    def setUp(self):
        self.xlsx_bytes = TableExporter(
            data=self.testset,
            data_getters=map(lambda _: _[1], self.getters),
            headers=map(lambda _: _[0], self.getters),
        ).get_xlsx_content()

    def test_gen_xlsx(self):
        ws = load_workbook(self.xlsx_bytes).active

        for col_num, (col_name, _) in enumerate(self.getters):
            self.assertEqual(ws.rows[0][col_num].value, col_name)

        for row_num, entry in enumerate(ws.rows[1:]):
            test_entry = self.testset[row_num]
            for col_num, (_, getter) in enumerate(self.getters):
                self.assertEqual(entry[col_num].value, getter(test_entry))


class VCardTest(unittest.TestCase):
    testset = [
            (b'asfssad', b'asfssad\0\0\0\0\0\0\0\0\0'),
            (b'asfssadasfssadx', b'asfssadasfssadx\0'),
            (b'', b'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0'),
            (b'asfssadasfssadxx', b'asfssadasfssadxx\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0'),
    ]

    negative_testset = ('str', 6, 1.5, None)

    def test_pad(self):
        for inp, outp in self.testset:
            self.assertEqual(pad(inp), outp)

        for inp in self.negative_testset:
            self.assertRaises(AssertionError, pad, inp)
