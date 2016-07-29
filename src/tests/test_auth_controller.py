import json

from GDGUkraine.model import Admin, Place
from GDGUkraine.model import metadata

from tests.helper import orm_session, Session
from blueberrypy.testing import ControllerTestCase


@orm_session
def populate_db():
    session = Session()

    gdg_host = Place(city='Gotham', name='Superheroes', show='1')
    session.add(gdg_host)

    vasia_pupkin = Admin(email='test@gdg.org.ua', godmode=True,
                         place=gdg_host.id)

    session.add(vasia_pupkin)
    session.commit()


class UserRESTAPITest(ControllerTestCase):
    def getJSON(self, *args, **kwargs):
        status, headers, body = self.getPage(*args, **kwargs)
        self.json_result = json.loads(body.decode('utf-8'))
        return status, headers, self.json_result

    def assertJSON(self, value, tmp_resp=None):
        assert isinstance(
            value, (dict, list)) or isinstance(
                value, type(tmp_resp)), ('This test is meant to test '
                                         'JSON against dict or list')

        if tmp_resp is None:
            tmp_resp = self.json_result

        if isinstance(value, dict):
            assert len(value) == len(tmp_resp)
            for k, v in value.items():
                self.assertJSON(v, tmp_resp[k])
        elif isinstance(value, list):
            assert len(value) == len(tmp_resp)
            for i, v in enumerate(value):
                self.assertJSON(v, tmp_resp[i])
        else:
            assert value == tmp_resp

    @orm_session
    def setUp(self):
        metadata.create_all()
        populate_db()

    @orm_session
    def tearDown(self):
        metadata.drop_all()

    def test_authenticate_user(self):
        # Authenticate as a fake user
        self.getJSON('/api/info')
        self.assertStatus(401)
        print('401 asserted, start checking json')
        self.assertJSON({'reason': 'Unauthorized', 'code': 401,
                         'message': 'Please authorize'})
        self.getPage('/auth/fake-login')
        self.assertStatus(200)
        status, headers, json_res = self.getJSON('/api/info')
        self.assertStatus(200)
        assert json_res['user']['name'] == 'Vasia Pupkin'
        assert json_res['user']['email'] == 'test@gdg.org.ua'
        assert json_res['user']['godmode'] is True
        assert json_res['user']['admin'] is True
