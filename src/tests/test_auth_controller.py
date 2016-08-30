from unittest.mock import MagicMock

from GDGUkraine.lib.testing import TestCase, SessionMock, mock_session
from GDGUkraine.model import (
        Admin, Place,
        metadata
)

from tests.helper import orm_session, Session


@orm_session
def populate_db():
    session = Session()

    gdg_host = Place(city='Gotham', name='Superheroes', show='1')
    session.add(gdg_host)

    vasia_pupkin = Admin(email='test@gdg.org.ua', godmode=True,
                         place=gdg_host.id)

    session.add(vasia_pupkin)
    session.commit()


class UserRESTAPITest(TestCase):
    @orm_session
    def setUp(self):
        metadata.create_all()
        populate_db()

    @orm_session
    def tearDown(self):
        metadata.drop_all()

    def test_authenticate_user(self):
        self.getJSON('/api/info')
        self.assertStatus(401)
        self.assertJSON({'reason': 'Unauthorized', 'code': 401,
                         'message': 'Please authorize'})

        sess_mock = SessionMock()
        sess_mock['admin_user'] = {'email': 'test@gdg.org.ua', 'filter_place': None,
                                   'googler_id': 777, 'godmode': True, 'place': None}
        sess_mock['google_oauth_token'] = MagicMock()
        sess_mock['google_user'] = {
            'given_name': 'Petryk',
            'gender': 'male',
            'link': 'https://plus.google.com/+SvyatoslavSydorenko',
            'picture': 'https://www.wired.com/wp-content/uploads/blogs'
                       '/wiredenterprise/wp-content/uploads/2012/06'
                       '/Screen-shot-2012-06-18-at-10.32.45-AM.png',
            'name': 'Petryk Piatochkin',
            'hd': 'gdg.org.ua',
            'email': 'test@gdg.org.ua',
            'id': '133555540822907599802',
            'locale': 'uk',
            'verified_email': True,
            'family_name': 'Piatochkin'
        }
        with mock_session(session=sess_mock):
            status, headers, json_res = self.getJSON('/api/info')
        self.assertStatus(200)
        json_user = json_res['user']
        self.assertEquals(json_user['name'], 'Petryk Piatochkin')
        self.assertEquals(json_user['email'], 'test@gdg.org.ua')
        self.assertTrue(json_user['godmode'])
        self.assertTrue(json_user['admin'])
        # self.assertJSON({'user': sess_mock['google_user']})
