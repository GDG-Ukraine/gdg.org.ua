import cherrypy


__all__ = ['AuthorizeTool']


class AuthorizeTool(cherrypy.Tool):

    def __init__(self):
        cherrypy.Tool.__init__(
            self, 'before_handler', self._fetch, priority=20
        )

    def _setup(self):
        cherrypy.Tool._setup(self)
        cherrypy.request.hooks.attach(
            'on_end_resource', self._cleanup, priority=80
        )

    def _fetch(self):
        session = cherrypy.session

        google_oauth_token = session.get('google_oauth_token')
        google_user = session.get('google_user')
        admin_user = session.get('admin_user')

        if not google_user:
            raise cherrypy.HTTPError(401, 'Please authorize')
        if not admin_user:
            raise cherrypy.HTTPError(403, 'Forbidden')

        cherrypy.request.admin_user = admin_user
        cherrypy.request.google_user = google_user
        cherrypy.request.google_oauth_token = google_oauth_token

    def _cleanup(self):
        cherrypy.request.admin_user = None
        cherrypy.request.google_user = None
