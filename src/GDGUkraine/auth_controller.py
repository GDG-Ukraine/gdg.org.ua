import cherrypy
import logging

from cherrypy import HTTPError, HTTPRedirect

from requests_oauthlib import OAuth2Session


logger = logging.getLogger(__name__)

client_id = '1012272991665.apps.googleusercontent.com'
client_secret = 'baKsIdO1RgRZVfoEetx1oTjT'
redirect_uri = 'http://localhost:8080/auth/google'

authorization_base_url = "https://accounts.google.com/o/oauth2/auth"
token_url = "https://accounts.google.com/o/oauth2/token"

scope = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile"
]

google = OAuth2Session(client_id, scope=scope, redirect_uri=redirect_uri)

# Redirect user to Google for authorization
authorization_url, state = google.authorization_url(
    authorization_base_url,
    # offline for refresh token
    # force to always make user click authorize
    access_type="offline", approval_prompt="force")


class AuthController:
    """AuthController implements authentication via Google's OAuth2"""
    def __init__(self, arg=None):
        super(AuthController, self).__init__()
        self.arg = arg

    @cherrypy.expose
    def google(self, *args, **kwargs):
        req = cherrypy.request
        # logger.debug(args)
        # logger.debug(kwargs)
        cherrypy.session['google_oauth'] = kwargs
        # import ipdb; ipdb.set_trace()
        # forward_url = req.headers.get("Referer", "/")
        # raise HTTPRedirect('http://google.com/{0}'.format(forward_url))
        # raise HTTPRedirect(authorization_url)
        redirect_response = '{}?{}'.format(cherrypy.url(), req.query_string)
        google.fetch_token(token_url, client_secret=client_secret,
                           authorization_response=redirect_response)
        r = google.get('https://www.googleapis.com/oauth2/v1/userinfo')
        cherrypy.session['google_user'] = r.content
        if cherrypy.session.get('auth_redirect'):
            raise HTTPRedirect(cherrypy.session['auth_redirect'])
        # elif
        return r.content

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

        raise HTTPRedirect(authorization_url)
