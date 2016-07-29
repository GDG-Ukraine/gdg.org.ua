from datetime import date

from GDGUkraine.model import User
from GDGUkraine.model import metadata

from tests.helper import orm_session, Session
from blueberrypy.testing import ControllerTestCase


@orm_session
def populate_db():
    session = Session()

    alice = User(displayname='alice',
                 email='alice@wonderland.com',
                 password='alicepassword',
                 sex='f',
                 phone='23452342',
                 birthday=date(1985, 3, 26))

    bob = User(displayname='bob',
               email='bob@example.com',
               password='bobpassword',
               sex='m',
               phone='99990000',
               birthday=date(1978, 4, 27))

    session.add(alice)
    session.add(bob)
    session.commit()


class UserRESTAPITest(ControllerTestCase):
    @orm_session
    def setUp(self):
        metadata.create_all()
        populate_db()

    @orm_session
    def tearDown(self):
        metadata.drop_all()

    def test_create_user(self):
        self.fail()

    def test_show_user(self):
        self.fail()

    def test_update_user(self):
        self.fail()

    def test_delete_user(self):
        self.fail()
