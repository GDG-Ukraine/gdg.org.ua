from GDGUkraine.lib.testing import TestCase, mock_session, user_session_factory
from GDGUkraine.model import (
        Admin, Place,
        metadata
)

from .helper import orm_session, Session


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

        sess_mock = user_session_factory({
            'admin_user': {'godmode': True},
            'google_user': {
                'name': 'Petryk Piatochkin',
                'email': 'test@gdg.org.ua',
            }
        })
        with mock_session(session=sess_mock):
            status, headers, json_res = self.getJSON('/api/info')
        self.assertStatus(200)

        json_user = json_res['user']
        self.assertEquals(json_user['name'], 'Petryk Piatochkin')
        self.assertEquals(json_user['email'], 'test@gdg.org.ua')
        self.assertTrue(json_user['godmode'])
        self.assertTrue(json_user['admin'])
        # self.assertJSON({'user': sess_mock['google_user']})

