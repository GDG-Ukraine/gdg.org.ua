from .plugins import register_plugins as register_auth_plugin
from .oauth import register_plugins as register_oauth_plugin
from .lib.tools import register_tools


__version__ = "1.0"

register_auth_plugin()
register_oauth_plugin()
register_tools()
