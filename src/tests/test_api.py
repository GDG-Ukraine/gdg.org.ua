try:
    import unittest2 as unittest
except ImportError:
    import unittest

from GDGUkraine import api
from GDGUkraine.model import Admin, Place, Event, User, EventParticipant

from tests.helper import DBTestFixture, orm_session, Session


class APITest(DBTestFixture, unittest.TestCase):

    @orm_session
    def setUp(self):
        super().setUp()

        session = Session()

        alice = User(nickname='alice',
                     name='Alice',
                     surname='Johns',
                     email='alice@wonderland.com',
                     gender='female')

        bob = User(nickname='bob',
                   name='Bob',
                   surname='Williams',
                   email='bob@example.com',
                   gender='male')

        gdg_host = Place(city='Gotham', name='Superheroes', show='1')

        vasia_pupkin = Admin(email='test@gdg.org.ua', godmode=True,
                             place=gdg_host)

        conf = Event(title='GDG Con', url='https://gdg.org.ua',
                     desc='Some event', gplus_event_id='11111111111111111',
                     host_gdg=gdg_host)

        epa = EventParticipant(user=alice, event=conf)
        epb = EventParticipant(user=bob, event=conf)

        session.add_all([gdg_host, vasia_pupkin, conf, alice, bob, epa, epb])
        session.commit()

    # test_get_all_posts

    @orm_session
    def test_get_place_by_id(self):
        session = Session()
        loc = api.get_place_by_id(session, 1)
        self.assertEquals(loc.city, 'Gotham')
        self.assertEquals(loc.name, 'Superheroes')

    @orm_session
    def test_find_user_by_id(self):
        session = Session()
        alice = api.find_user_by_id(session, 1)
        self.assertEqual(alice.nickname, "alice")
        self.assertEqual(alice.email, 'alice@wonderland.com')
        self.assertEqual(alice.gender, 'female')
        self.assertEqual(alice.surname, 'Johns')

    @orm_session
    def test_find_user_by_email(self):
        session = Session()
        bob = api.find_user_by_email(session, 'bob@example.com')
        self.assertEqual(bob.nickname, 'bob')
        self.assertEqual(bob.email, 'bob@example.com')
        self.assertEqual(bob.gender, 'male')
        self.assertEqual(bob.name, 'Bob')

    @orm_session
    def test_delete_user_by_id(self):
        session = Session()
        self.assertEqual(api.delete_user_by_id(session, 1), 1)
        self.assertIsNone(api.find_user_by_id(session, 1))

    @orm_session
    def test_find_admin_by_email(self):
        session = Session()
        vasia = api.find_admin_by_email(session, 'test@gdg.org.ua')
        self.assertIs(vasia.godmode, True)

    @orm_session
    def test_find_event_by_id(self):
        session = Session()
        con = api.find_event_by_id(session, 1)
        self.assertEquals(con.title, 'GDG Con')
        self.assertEquals(con.gplus_event_id, '11111111111111111')
        self.assertEquals(con.host_gdg.city, 'Gotham')

    @orm_session
    def test_get_all_users(self):
        session = Session()
        usrs = api.get_all_users(session)
        self.assertEqual(usrs[0].nickname, "alice")
        self.assertEqual(usrs[0].email, 'alice@wonderland.com')
        self.assertEqual(usrs[0].gender, 'female')
        self.assertEqual(usrs[0].surname, 'Johns')

    @orm_session
    def test_get_users_by_ids(self):
        session = Session()
        alice, *_ = api.get_users_by_ids(session, [1])
        self.assertEqual(alice.nickname, "alice")
        self.assertEqual(alice.email, 'alice@wonderland.com')
        self.assertEqual(alice.gender, 'female')
        self.assertEqual(alice.surname, 'Johns')

    # def test_get_event_registrations_by_ids(session, reg_ids):
    # def test_get_event_registration_by_id(session, reg_id):
    # def test_get_all_gdg_places(session, filtered=False):
    # def test_find_event_by_id(session, id):
    # def test_find_host_gdg_by_event(session, event):
    # def test_get_all_events(session, lim=None, hide_closed=False):
    # def test_delete_event_by_id(session, id):
    # def test_find_participants_by_event(session, e):
    # def test_find_events_by_user(session, u):
    # def test_get_event_registration(session, uid, eid):
    # def test_get_event_registrations(session, event_id):
    # def test_find_invitation_by_code(session, code):
