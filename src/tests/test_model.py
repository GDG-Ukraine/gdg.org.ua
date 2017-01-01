try:
    import unittest2 as unittest
except ImportError:
    import unittest

from GDGUkraine.model import User

from tests.helper import DBTestFixture, orm_session, Session


class UserTest(DBTestFixture, unittest.TestCase):

    @orm_session
    def test_constructor(self):

        session = Session()

        user = User(nickname='alice',
                    name='Alice',
                    surname='Johns',
                    email='alice@wonderland.com',
                    gender='female')

        session.add(user)
        session.commit()
