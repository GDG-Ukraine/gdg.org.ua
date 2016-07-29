try:
    import unittest2 as unittest
except ImportError:
    import unittest
from datetime import date

from GDGUkraine.model import User

from tests.helper import DBTestFixture, orm_session, Session


class UserTest(DBTestFixture, unittest.TestCase):

    @orm_session
    def test_constructor(self):

        session = Session()

        user = User(displayname='alice in wonderland',
                    email='alice@wonderland.com',
                    password='wonderlandpass',
                    sex='m',
                    date_of_birth=date.today())

        session.add(user)
        session.commit()

    @orm_session
    def test_passwords(self):

        session = Session()

        user = User(displayname='displayname',
                    email='abc@example.com',
                    sex='m',
                    date_of_birth=date(1980, 1, 1))
        user.password = 'password'
        session.add(user)
        session.commit()

        self.assertTrue(user.validate_password('password'))
        from base64 import b64decode
        self.assertEqual(
            user._User__encrypt_password('password', b64decode(user.salt)),
            user.password)
