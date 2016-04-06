import cherrypy
import logging

from cherrypy import HTTPError

from blueberrypy.template_engine import get_template

from .api import get_all_posts


logger = logging.getLogger(__name__)


class BlogController:
    """BlogController implements authentication via Google's OAuth2"""

    @cherrypy.expose
    def index(self):
        from pprint import pprint
        posts = get_all_posts(cherrypy.request.orm_session)
        pprint(posts)
        if posts:
            tmpl = get_template("blog/posts.html")
            return tmpl.render(posts=posts)
        raise HTTPError(404)

    default = index
