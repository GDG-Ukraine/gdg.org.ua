try:
    import unittest2 as unittest
except ImportError:
    import unittest

import cherrypy
from blueberrypy.testing import ControllerTestCase

from openpyxl import load_workbook

from GDGUkraine import api, model
from GDGUkraine.lib.utils.url import base_url, url_for
from GDGUkraine.lib.utils.table_exporter import (
    gen_participants_xlsx,
    event_parsers
)

from tests.helper import DBTestFixture, orm_session, Session


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


class TableExporterTest(DBTestFixture, unittest.TestCase):
    def setUp(self):
        super().setUp()

        # Detecting the number of Nickname column
        for num, _ in enumerate(event_parsers):
            if _[0] == 'Nickname':
                self.nickname_col_num = num
                break

        session = Session()

        user = model.User(
            name='Serhii',
            surname='Brin',
            nickname='googler_zero',
            email='serhii@google.com',
            gender='male',
        )
        session.add(user)

        host = model.Place()
        session.add(host)
        session.commit()

        event = model.Event(
            url='https://plus.google.com/events/xxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
            title='Meeting Brin',
            desc='Come and feel yourself Serhii\'s friend!',
            host_gdg_id=host.id,
        )
        session.add(event)
        session.commit()

        self.event_registration = model.EventParticipant(
            googler_id=user.id,
            event_id=user.id,
        )
        session.add(self.event_registration)
        session.commit()

        event = api.find_event_by_id(session, event.id)
        self.event_participations = api.find_participants_by_event(session,
                                                                   event)

    def tearDown(self):
        super().tearDown()

    @orm_session  # closes session on function finish
    def test_gen_xlsx(self):
        xls_file = gen_participants_xlsx(self.event_participations)
        wb = load_workbook(xls_file)
        ws = wb.active
        self.assertEqual(ws.rows[1][self.nickname_col_num].value,
                         self.event_registration.user.nickname)
