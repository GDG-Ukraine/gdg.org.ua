"""Toolset for testing GDGUkraine app"""

from unittest.mock import patch, MagicMock

from cherrypy.lib.sessions import Session, RamSession

from blueberrypy.testing import ControllerTestCase

from ..utils import json


DUMMY_ADMIN_USER = {'email': 'test@gdg.org.ua', 'filter_place': None,
                    'googler_id': 777, 'godmode': True, 'place': None}

DUMMY_GOOGLE_USER = {
    'given_name': 'Petryk',
    'gender': 'male',
    'link': 'https://plus.google.com/+PetrykPiatochkin',
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


class TestCase(ControllerTestCase):
    """Implements extended test case with json testing enabled"""
    def postJSON(self, url, payload, *args, **kwargs):
        status, headers, body = self.getPage(
            url, method='POST', body=json.dumps(payload),
            headers=[('Content-Type', 'application/json'), ], *args, **kwargs)
        self.json_result = json.loads(body.decode('utf-8'))
        return status, headers, self.json_result

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


class SessionMock(RamSession):
    """Implements dummy session object"""


def user_session_factory(session_data=None):
    """Returns dummy session object with admin user data filled by default

    Args:
        `session_data` should be dict-like, it's used to override defaults
    """
    assert session_data is None or isinstance(session_data, dict)

    sess = SessionMock()
    sess['admin_user'] = DUMMY_ADMIN_USER.copy()
    sess['google_user'] = DUMMY_GOOGLE_USER.copy()
    sess['google_oauth_token'] = MagicMock()

    if session_data:
        sess.update(session_data.copy())

    return sess


def mock_session(session=None):
    """Monkey-patches cherrypy.session objects while testing

    Args:
        `session` is an instance of cherrypy.lib.sessions.Session

    Usage:
        from GDGUkraine.lib.testing import mock_session
        ...
        with mock_session():
            your_resuest_to_handler_accessing_session()
    """
    assert session is None or isinstance(session, Session)

    if not session:
        session = SessionMock()

    return patch('cherrypy.session', session, create=True)
