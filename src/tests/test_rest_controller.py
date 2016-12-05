from GDGUkraine.lib.testing import TestCase, mock_session, user_session_factory
from GDGUkraine.model import Admin, Place, Event, User, EventParticipant
from GDGUkraine.model import metadata

from tests.helper import orm_session, Session


@orm_session
def populate_db():
    session = Session()

    alice = User(nickname='alice',
                 name='Alice',
                 surname='Johns',
                 email='alice@wonderland.com',
                 gender='female')

    gdg_host = Place(city='Gotham', name='Superheroes', show='1')

    vasia_pupkin = Admin(email='test@gdg.org.ua', godmode=True, place=gdg_host)

    conf = Event(title='GDG Con', url='https://gdg.org.ua', desc='Some event',
                 gplus_event_id='11111111111111111', host_gdg=gdg_host)

    epa = EventParticipant(user=alice, event=conf)

    session.add_all([gdg_host, vasia_pupkin, conf, alice, epa])
    session.commit()


class EventRESTAPITest(TestCase):
    @orm_session
    def setUp(self):
        metadata.create_all()
        populate_db()

    @orm_session
    def tearDown(self):
        metadata.drop_all()

    def test_record_visit(self):
        reg_id = 1
        with mock_session(session=user_session_factory()):
            status, headers, json_res = self.postJSON('/api/events/{reg_id}/check-in'.format(reg_id=reg_id),
                                                      payload={})
        self.assertStatus(200)


# class UserRESTAPITest(TestCase):
#     @orm_session
#     def setUp(self):
#         metadata.create_all()
#         populate_db()
#
#     @orm_session
#     def tearDown(self):
#         metadata.drop_all()
#
#     def test_create_user(self):
#         self.fail()
#
#     def test_show_user(self):
#         self.fail()
#
#     def test_update_user(self):
#         self.fail()
#
#     def test_delete_user(self):
#         self.fail()
