from cerberus import Validator
from .schema import regform_schema


regform_validator = Validator(regform_schema, allow_unknown=True)
__all__ = ['regform_validator', ]
