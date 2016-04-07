from cerberus import Validator

from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

# TODO: consider converting this package into plugin+tool, since global config
# entries aren't available, when it's being loaded, resulting in hardcoding
with open('src/GDGUkraine/lib/validation/regform_schema.yml', 'r') as _:
    regform_schema = load(_, Loader)

regform_validator = Validator(regform_schema, allow_unknown=True)
__all__ = ['regform_validator', ]
