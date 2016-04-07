import importlib


__all__ = [
    'import_first_of',
    'import_first_from',
    'json',
    'yaml',
]

json = None
for pkg in ['ujson', 'yajl', 'simplejson', 'cjson', 'json']:
    try:
        json = importlib.import_module(pkg)
    except:
        pass
    else:
        break


def import_first_of(pkgs):
    if isinstance(pkgs, str):
        pkgs = [pkgs]
    else:
        try:
            iter(pkgs)
        except Exception as exc:
            raise ImportError from exc

    for pkg in pkgs:
        try:
            return importlib.import_module(pkg)
        except ImportError:
            pass

    raise ImportError


def import_first_from(module, attrs):
    if isinstance(attrs, str):
        attrs = [attrs]
    else:
        try:
            iter(attrs)
        except Exception as exc:
            raise ImportError from exc

    for attr in attrs:
        try:
            return getattr(module, attr)
        except AttributeError:
            pass

    raise ImportError


json = import_first_of(['ujson', 'yajl', 'simplejson', 'cjson', 'json'])

yaml = import_first_of('yaml')
