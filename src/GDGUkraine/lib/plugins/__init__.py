from .urlmap import register as register_urlmap_plugin
from .oauth import register as register_oauth_plugin


def register_plugins():
    # Register the plugin in CherryPy:
    register_urlmap_plugin()
    register_oauth_plugin()
