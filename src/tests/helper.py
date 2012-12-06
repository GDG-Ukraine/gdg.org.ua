import functools

from sqlalchemy import *
from sqlalchemy.orm import sessionmaker, scoped_session

from testconfig import config as testconfig

from GDGUkraine.model import *
from GDGUkraine.model import metadata


engine = engine_from_config(testconfig['sqlalchemy_engine'], '')
Session = scoped_session(sessionmaker(engine))
metadata.bind = engine


def orm_session(func):
    def _orm_session(*args, **kwargs):
        session = Session()
        try:
            return func(*args, **kwargs)
        except:
            raise
        finally:
            session.close()
    return functools.update_wrapper(_orm_session, func)


class DBTestFixture(object):

    def setUp(self):
        metadata.create_all()

        super(DBTestFixture, self).setUp()

    def tearDown(self):
        metadata.drop_all()

        super(DBTestFixture, self).tearDown()