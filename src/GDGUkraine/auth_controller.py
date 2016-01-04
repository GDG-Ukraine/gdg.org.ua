import cherrypy
import json
import logging

from cherrypy import HTTPError, HTTPRedirect

from blueberrypy.util import to_collection

from requests_oauthlib import OAuth2Session
from oauthlib.oauth2.rfc6749.errors import (MissingCodeError,
                                            MismatchingStateError)

from .api import find_admin_by_email


logger = logging.getLogger(__name__)

client_id = '1012272991665.apps.googleusercontent.com'
client_secret = 'baKsIdO1RgRZVfoEetx1oTjT'
redirect_uri = 'http://localhost:8080/auth/google'

authorization_base_url = "https://accounts.google.com/o/oauth2/auth"
token_url = "https://accounts.google.com/o/oauth2/token"

scope = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    # Send an email message
    "https://www.googleapis.com/auth/gmail.compose",
    # Create a new file on Google Drive
    "https://www.googleapis.com/auth/drive.file",
]


class AuthController:
    """AuthController implements authentication via Google's OAuth2"""
    def __init__(self, arg=None):
        super(AuthController, self).__init__()
        self.arg = arg

    @cherrypy.expose
    def google(self, *args, **kwargs):
        req = cherrypy.request
        orm_session = req.orm_session
        try:
            google = OAuth2Session(client_id, redirect_uri=redirect_uri,
                                   state=cherrypy.session['oauth_state'])

            redirect_response = '{}?{}'.format(cherrypy.url(),
                                               req.query_string)
            cherrypy.session['google_oauth_token'] = google.fetch_token(
                token_url, client_secret=client_secret,
                authorization_response=redirect_response)

            cherrypy.session['google_user'] = google.\
                get('https://www.googleapis.com/oauth2/v1/userinfo').json()
            cherrypy.session['admin_user'] = to_collection(find_admin_by_email(
                orm_session,
                cherrypy.session['google_user']['email']))
            cherrypy.session['google_oauth'] = kwargs

            if cherrypy.session.get('auth_redirect'):
                print('redirect after auth')
                logger.debug('redirect after auth')
                raise HTTPRedirect(cherrypy.session['auth_redirect'])
            else:
                raise HTTPRedirect('/')
            return json.dumps(cherrypy.session['admin_user'])
        except MissingCodeError:
            raise HTTPError(401, 'Error: {}'.format(kwargs.get('error')))
        except (MismatchingStateError, KeyError):
            raise HTTPRedirect('/auth')

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

        google = OAuth2Session(client_id, scope=scope,
                               redirect_uri=redirect_uri)

        # Redirect user to Google for authorization
        authorization_url, cherrypy.session['oauth_state'] = google.\
            authorization_url(authorization_base_url,
                              # offline for refresh token
                              # force to always make user click authorize
                              access_type="offline", approval_prompt="force")

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

        if return_url.stratswith(['/', 'https://', 'http://']) \
           and not return_url.startswith('/auth'):
            raise HTTPRedirect(return_url)

        raise HTTPRedirect('/')
