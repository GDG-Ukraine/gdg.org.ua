import cherrypy as cp


def is_authorized():
    return isinstance(cp.session.get('admin_user'), dict) and \
        isinstance(cp.session.get('google_oauth'), dict) and \
        isinstance(cp.session.get('google_user'), dict)
