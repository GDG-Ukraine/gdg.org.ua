# Note: lots of stuff is copy-pasted from cherrypy._cperror
# and needs refactoring

from cgi import escape as _escape
from sys import exc_info as _exc_info
from traceback import format_exception as _format_exception

from cherrypy import HTTPError
from cherrypy.lib import httputil as _httputil
from cherrypy._cpcompat import tonative


class ExtendedHTTPError(HTTPError):
    def __init__(self, status=500, message=None, errors=None):
        self._errors = errors
        super().__init__(status, message)

    @property
    def errors(self):
        return self._errors

    def get_error_page(self, *args, **kwargs):
        return get_error_page(errors=self.errors, *args, **kwargs)


class InvalidFormDataError(ExtendedHTTPError):
    def __init__(self, errors=None):
        super().__init__(400, 'Invalid request', errors=errors)


_HTTPErrorTemplate = '''<!DOCTYPE html PUBLIC
"-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"></meta>
    <title>%(status)s</title>
    <style type="text/css">
    #powered_by {
        margin-top: 20px;
        border-top: 2px solid black;
        font-style: italic;
    }

    #traceback {
        color: red;
    }
    </style>
</head>
    <body>
        <h2>%(status)s</h2>
        <p>%(message)s</p>
        <pre id="traceback">%(traceback)s</pre>
    <div id="powered_by">
      <span>
        Powered by <a href="http://www.cherrypy.org">CherryPy %(version)s</a>
      </span>
    </div>
    </body>
</html>
'''


def get_error_page(status, errors=None, **kwargs):
    """Return an HTML page, containing a pretty error response.

    status should be an int or a str.
    kwargs will be interpolated into the page template.
    """
    import cherrypy

    try:
        code, reason, message = _httputil.valid_status(status)
    except ValueError:
        raise cherrypy.HTTPError(500, _exc_info()[1].args[0])

    # We can't use setdefault here, because some
    # callers send None for kwarg values.
    if kwargs.get('status') is None:
        kwargs['status'] = "%s %s" % (code, reason)
    if kwargs.get('message') is None:
        kwargs['message'] = message
    if kwargs.get('traceback') is None:
        kwargs['traceback'] = ''
    if kwargs.get('version') is None:
        kwargs['version'] = cherrypy.__version__

    for k, v in kwargs.items():
        if v is None:
            kwargs[k] = ""
        else:
            kwargs[k] = _escape(kwargs[k])

    # Use a custom template or callable for the error page?
    pages = cherrypy.serving.request.error_page
    error_page = pages.get(code) or pages.get('default')

    # Default template, can be overridden below.
    template = _HTTPErrorTemplate
    if error_page:
        try:
            if hasattr(error_page, '__call__'):
                # The caller function may be setting headers manually,
                # so we delegate to it completely. We may be returning
                # an iterator as well as a string here.
                #
                # We *must* make sure any content is not unicode.
                result = error_page(errors=errors, **kwargs)
                if cherrypy.lib.is_iterator(result):
                    from cherrypy.lib.encoding import UTF8StreamEncoder
                    return UTF8StreamEncoder(result)
                elif isinstance(result, cherrypy._cpcompat.unicodestr):
                    return result.encode('utf-8')
                else:
                    if not isinstance(result, cherrypy._cpcompat.bytestr):
                        raise ValueError(
                            'error page function did not '
                            'return a bytestring, unicodestring or an '
                            'iterator - returned object of type {}.'
                            .format(type(result).__name__))
                    return result
            else:
                # Load the template from this path.
                template = tonative(open(error_page, 'rb').read())
        except:
            e = _format_exception(*_exc_info())[-1]
            m = kwargs['message']
            if m:
                m += "<br />"
            m += "In addition, the custom error page failed:\n<br />%s" % e
            kwargs['message'] = m

    response = cherrypy.serving.response
    response.headers['Content-Type'] = "text/html;charset=utf-8"
    result = template % kwargs
    return result.encode('utf-8')
