import cherrypy
import logging

from cherrypy import HTTPError, HTTPRedirect

from blueberrypy.util import to_collection

from oauthlib.oauth2.rfc6749.errors import (MissingCodeError,
                                            MismatchingStateError)

from .api import find_admin_by_email
from .utils import pub, url_for_class


logger = logging.getLogger(__name__)


class AuthController:
    """AuthController implements authentication via Google's OAuth2"""

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def google(self, **kwargs):
        req = cherrypy.request
        orm_session = req.orm_session
        try:
            # Aquire API token internally
            pub('oauth-token')

            # Aquire OAuth2Session instance, built with token
            google_api = pub('google-api')

            cherrypy.session['google_user'] = google_api.get(
                    'https://www.googleapis.com/oauth2/v1/userinfo').json()

            cherrypy.session['admin_user'] = to_collection(find_admin_by_email(
                orm_session,
                cherrypy.session['google_user']['email']))
            cherrypy.session['google_oauth'] = kwargs

            if cherrypy.session.get('auth_redirect'):
                print('redirect after auth')
                logger.debug('redirect after auth')
                raise HTTPRedirect(cherrypy.session['auth_redirect'])
            else:
                raise HTTPRedirect(url_for_class('controller.Root'))

            return cherrypy.session['admin_user']
        except MissingCodeError as mce:
            raise HTTPError(401,
                            'Error: {}'.format(kwargs.get('error'))) from mce
        except (MismatchingStateError, KeyError) as wrong_state:
            raise HTTPRedirect(
                    url_for_class('controller.Root.auth')) from wrong_state

    # index = google

    @cherrypy.expose
    def index(self, return_url=None):
        return_url = (return_url
                      if return_url
                      else cherrypy.request.headers.get('Referer'))

        if return_url is not None and \
           return_url.stratswith(['/', 'https://', 'http://']) \
           and not return_url.startswith('/auth'):
            cherrypy.session['auth_redirect'] = return_url

        authorization_url = pub('oauth-url')

        raise HTTPRedirect(authorization_url)

    @cherrypy.expose
    def logout(self, return_url=None):
        for key in ['google_oauth', 'google_user',
                    'admin_user', 'auth_redirect']:
            if cherrypy.session.get(key):
                del cherrypy.session[key]

        return_url = (return_url
                      if return_url
                      else cherrypy.request.headers.get('Referer', '/'))

        if return_url.startswith(['/', 'https://', 'http://']) \
           and not return_url.startswith('/auth'):
            raise HTTPRedirect(return_url)

        raise HTTPRedirect(url_for_class('controller.Root'))
