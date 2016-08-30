from unittest.mock import patch

from cherrypy.lib.sessions import Session, RamSession

from blueberrypy.testing import ControllerTestCase

from ..utils import json


class TestCase(ControllerTestCase):
    """Implements extended test case with json testing enabled"""
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


def mock_session(session=None):
    """Monkey-patches cherrypy.session objects while testing

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
