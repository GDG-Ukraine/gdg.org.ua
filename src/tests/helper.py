import functools

from blueberrypy.config import BlueberryPyConfiguration

from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker, scoped_session

from testconfig import config as testconfig

from GDGUkraine.model import metadata


config = BlueberryPyConfiguration(
    app_config=testconfig,
    # Don't update config from env var! This may lead to losing the DB!!111
    env_var_name=None,
)

engine = engine_from_config(config.sqlalchemy_config['sqlalchemy_engine'], '')
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
