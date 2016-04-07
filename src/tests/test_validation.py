import unittest
from unittest.mock import MagicMock
from GDGUkraine.lib.validation import regform_validator
from GDGUkraine.lib.validation.field_validators import (
    email as email_validator_func,
    url as url_validator_func,
)


class ValidatorsTests(unittest.TestCase):
    """ Set of tests to check validation rules """

    def test_regform_validator(self):
        testsuite = [
            {
                'data': {
                    'additional_info': 'Some text',
                    'company': 'Test company',
                    'email': 'user@example.com',
                    'english_knowledge': 'intermediate',
                    'events_visited': 'IO Extended 2012',
                    'experience_desc': 'Some experience description',
                    'gender': 'male',
                    'gplus': '1000000000042',
                    'hometown': 'Exampleville',
                    'interests': 'Some interests',
                    'name': 'John',
                    'nickname': 'johndoe',
                    'phone': '',
                    'position': 'Example position',
                    'surname': 'Doe',
                    't_shirt_size': 'l',
                    'www': 'http://site.example.com',
                },
                'result': True,
                'errors': {},
            },
            {
                'data': {
                    'additional_info': 'Some text',
                    'company': 'Test company',
                    'email': 'user@example.com',
                    'english_knowledge': 'intermediate',
                    'events_visited': 'IO Extended 2012',
                    'experience_desc': 'Some experience description',
                    'gender': 'male',
                    'gplus': '1000000000042',
                    'hometown': 'Exampleville',
                    'interests': 'Some interests',
                    'name': 'John',
                    'nickname': 'johndoe',
                    'phone': '',
                    'position': 'Example position',
                    'surname': 'Doe',
                    't_shirt_size': 'l',
                    'www': 'http://site.example.com',
                    'example_additiona;_field': 'some value',
                },
                'result': True,
                'errors': {},
            },
            {
                'data': {
                    'additional_info': 'Some text',
                    'company': (
                        'National Technical University Of Ukraine '
                        '"Kyiv Polytechnic Institute"'
                    ),
                    'email': 'user@example.com',
                    'english_knowledge': 'intermediate',
                    'events_visited': 'IO Extended 2012',
                    'experience_desc': 'Some experience description',
                    'gender': 'male',
                    'gplus': '1000000000042',
                    'hometown': 'Exampleville',
                    'interests': 'Some interests',
                    'name': 'John',
                    'nickname': 'johndoe',
                    'phone': '',
                    'position': 'Example position',
                    'surname': 'Doe',
                    't_shirt_size': 'l',
                    'www': 'http://site.example.com',
                },
                'result': False,
                'errors': {'company': 'max length is 64'},
            },
            {
                'data': {
                    'additional_info': 'Some text',
                    'company': (
                        'National Technical University Of Ukraine '
                        '"Kyiv Polytechnic Institute"'
                    ),
                    'english_knowledge': 'intermediate',
                    'events_visited': 'IO Extended 2012',
                    'experience_desc': 'Some experience description',
                    'gender': 'male',
                    'gplus': '1000000000042',
                    'hometown': 'Exampleville',
                    'interests': 'Some interests',
                    'name': 'John',
                    'nickname': 'johndoe',
                    'phone': '',
                    'position': 'Example position',
                    'surname': 'Doe',
                    't_shirt_size': 'big',
                    'www': 'site.example.com',
                },
                'result': False,
                'errors': {
                    'company': 'max length is 64',
                    't_shirt_size': 'unallowed value big',
                    'www': 'Invalid URL',
                    'email': 'required field',
                },
            },
        ]

        for record in testsuite:
            result = regform_validator.validate(record['data'])
            errors = regform_validator.errors
            self.assertEquals(result, record['result'])
            self.assertEquals(errors, record['errors'])


class FieldValidatorsTests(unittest.TestCase):
    """ Set of tests to check wether custom field validator functions
    perform correctly
    """

    def test_email_field_validator_positive(self):
        testdata = [
            'my.mail@example.com',
            'my.mail2.address@example.com',
            'my.mail+info@example.com',
            'my_mail@example.example2.com',
        ]
        errors_func = MagicMock(name='errors')
        for record in testdata:
            email_validator_func('email', record, errors_func)
        self.assertFalse(errors_func.called)

    def test_email_field_validator_negative(self):
        testdata = [
            'invalid@example',
            'invalid@example.',
            'invalid@.example',
            'just a text',
            'there_is_no_at_symbol.example',
            '://@example.com',
            'invalid@example..com',
        ]
        errors_func = MagicMock(name='errors')
        for record in testdata:
            email_validator_func('email', record, errors_func)
        self.assertTrue(errors_func.called)
        self.assertEquals(errors_func.call_count, len(testdata))

    def test_url_field_validator_positive(self):
        testdata = [
            'http://google.com',
            'http://google.com.ua',
            'http://linux.org',
            'https://gdg.org.ua/events/8/register',
        ]
        errors_func = MagicMock(name='errors')
        for record in testdata:
            url_validator_func('email', record, errors_func)
        self.assertFalse(errors_func.called)

    def test_url_field_validator_negative(self):
        testdata = [
            'google.com',
            '://google.com.ua',
            'http://linux',
            'https://gdg.o???rg.ua/events/8/register',
            'pony://gdg.o???rg.ua/events/8/register',
        ]
        errors_func = MagicMock(name='errors')
        for record in testdata:
            url_validator_func('email', record, errors_func)
        self.assertTrue(errors_func.called)
        self.assertEquals(errors_func.call_count, len(testdata))
