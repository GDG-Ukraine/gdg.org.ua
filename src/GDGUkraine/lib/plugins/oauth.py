# Borrowed from github.com:Lawouach/Twiseless/blob/master/lib/plugin/oauth.py

from collections import deque
from itertools import starmap

import cherrypy
from cherrypy.process.plugins import SimplePlugin

from requests_oauthlib import OAuth2Session

from ..utils.url import url_for_class

__all__ = ['OAuthEnginePlugin']


class GoogleAPI(OAuth2Session):
    """GoogleAPI is a wrapper for simplifying access to Google API"""
    google_api_url = 'https://www.googleapis.com{endpoint_uri}'

    def request(self, http_method, endpoint_uri, *args, **kwargs):
        """
        Patch any request's URL, prepending Google API URL if necessary
        """

        # Check whether it's an URL, skip if yes
        if not any(endpoint_uri.startswith(proto_base)
                   for proto_base in ['https://', 'http://']):
            # If it's a relative URI, make it absolute, starting with /
            if not endpoint_uri.startswith('/'):
                endpoint_uri = '/'.join(['', endpoint_uri])

            # Finally prepend Google API base URL
            endpoint_uri = self.google_api_url.format(
                endpoint_uri=endpoint_uri)

        # Do request
        return super().request(http_method,
                               endpoint_uri, *args, **kwargs)


class OAuthEnginePlugin(SimplePlugin):
    # https://github.com/google/oauth2client/blob/master/
    # oauth2client/client.py#L1874
    code_redirect_uri = 'postmessage'  # Do not touch! Magic!
    authorization_base_url = 'https://accounts.google.com/o/oauth2/auth'
    token_url = 'https://accounts.google.com/o/oauth2/token'
    refresh_url = token_url  # True for Google but not all providers.

    _channels = {
        'google-api': 'get_token_session',
        'oauth-url': 'get_auth_url',
        'oauth-token': 'fetch_token',
        'oauth-code-token': 'fetch_code_token',
    }

    def __init__(self, bus, consumer_key=None, consumer_secret=None):
        """
        Allows to interact with the underlying OAuth API
        """
        super().__init__(bus)

        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret

    def start(self):
        self.bus.log('Starting OAuth plugin')
        self._map_channels(self.bus.subscribe)  # Register all channels

    def stop(self):
        self.bus.log('Stopping down OAuth plugin')
        self._map_channels(self.bus.unsubscribe)  # Unregister all channels

    def _map_channels(self, callback):
        """Iterate over channels and apply a callable to them"""
        deque(starmap(callback,
                      starmap(lambda c, h: (c, getattr(self, h)),
                              self._channels.items())))

    @property
    def oauth_extra(self):
        return {
            'client_id': self.consumer_key,
            'client_secret': self.consumer_secret,
        }

    @property
    def redirect_url(self):
        return url_for_class('controller.Root.auth.google')

    @property
    def credentials(self):
        return cherrypy.config.get('google_oauth', {})

    @property
    def scope(self):
        return self.credentials.get('scope')

    @property
    def consumer_key(self):
        return self._consumer_key or self.credentials.get('id')

    @consumer_key.setter
    def consumer_key(self, value):
        self._consumer_key = value

    @consumer_key.deleter
    def consumer_key(self):
        del self._consumer_key

    @property
    def consumer_secret(self):
        return self._consumer_secret or self.credentials.get('secret')

    @consumer_secret.setter
    def consumer_secret(self, value):
        self._consumer_secret = value

    @consumer_secret.deleter
    def consumer_secret(self):
        del self._consumer_secret

    @property
    def oauth_state(self):
        return cherrypy.session['oauth_state']

    @oauth_state.setter
    def oauth_state(self, value):
        cherrypy.session['oauth_state'] = value

    @oauth_state.deleter
    def oauth_state(self):
        del cherrypy.session['oauth_state']

    @property
    def token(self):
        return cherrypy.session.get('google_oauth_token')

    @token.setter
    def token(self, value):
        cherrypy.session['google_oauth_token'] = value

    @token.deleter
    def token(self):
        del cherrypy.session['google_oauth_token']

    def get_auth_url(self):
        authorization_url, self.oauth_state = GoogleAPI(
            self.consumer_key, scope=self.scope,
            redirect_uri=self.redirect_url,
            auto_refresh_kwargs=self.oauth_extra,
            auto_refresh_url=self.refresh_url,
            token_updater=self.token,
        ).authorization_url(
            self.authorization_base_url,
            # offline for refresh token
            # force to always make user click authorize
            access_type='offline', approval_prompt='force')
        return authorization_url

    def _get_state_session(self):
        return GoogleAPI(
            self.consumer_key,
            state=self.oauth_state,
            redirect_uri=self.redirect_url,
            auto_refresh_kwargs=self.oauth_extra,
            auto_refresh_url=self.refresh_url,
            token_updater=self.token,
        )

    def _get_session(self):
        return GoogleAPI(
            self.consumer_key,
            redirect_uri=self.code_redirect_uri,
            auto_refresh_kwargs=self.oauth_extra,
            auto_refresh_url=self.refresh_url,
            token_updater=self.token,
        )

    def get_token_session(self):
        return GoogleAPI(
            self.consumer_key,
            token=self.token,
            auto_refresh_kwargs=self.oauth_extra,
            auto_refresh_url=self.refresh_url,
            token_updater=self.token,
        )

    def fetch_token(self):
        req = cherrypy.request
        redirect_response = '{}?{}'.format(self.redirect_url,
                                           req.query_string)
        self.token = self._get_state_session().fetch_token(
            self.token_url, client_secret=self.consumer_secret,
            authorization_response=redirect_response)
        return self.token

    def fetch_code_token(self, code):
        self.token = self._get_session().fetch_token(
            self.token_url, code=code, client_secret=self.consumer_secret)
        return self.token


def register():
    # Register the plugin in CherryPy:
    if not hasattr(cherrypy.engine, 'oauth'):
        cherrypy.engine.oauth = OAuthEnginePlugin(
            cherrypy.engine,
            cherrypy.config.get('google_oauth', {}).get('id'),
            cherrypy.config.get('google_oauth', {}).get('secret'))
