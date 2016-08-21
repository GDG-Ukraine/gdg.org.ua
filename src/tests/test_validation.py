import unittest
from GDGUkraine.lib.forms import (
    RegistrationForm, InputDict,
)


class ValidatorsTests(unittest.TestCase):
    """ Set of tests to check validation rules """

    def test_regform_validator(self):
        """Run different cases for form validation"""
        testsuite = [
            {
                'data': {
                    'additional_info': 'Some text',
                    'company': 'Test company',
                    'email': 'user@example.com',
                    'english_knowledge': 'intermediate',
                    'events_visited': 'IO Extended 2012',
                    'experience_level': 'newbie',
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
                    'experience_level': 'newbie',
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
                    'experience_level': 'newbie',
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
                'errors': {
                    'company': ['Field cannot be longer than 64 characters.'],
                },
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
                    'experience_level': 'newbie',
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
                    'company': ['Field cannot be longer than 64 characters.'],
                    'www': ['Invalid URL.'],
                    'email': ['This field is required.'],
                    't_shirt_size': ['Not a valid choice'],
                },
            },
            {
                'data': {
                    'additional_info': 'Some text',
                    'email': 'johndoe@example.com',
                    'company': 'Test company',
                    'english_knowledge': 'intermediate',
                    'events_visited': 'IO Extended 2012',
                    'experience_level': 'newbie',
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
                    't_shirt_size': 'm',
                    'www': '',
                },
                'result': True,
                'errors': {},
            },
        ]

        for record in testsuite:
            form = RegistrationForm(None, InputDict(record['data']))
            result = form.validate()
            errors = form.errors
            self.assertEquals(result, record['result'])
            self.assertEquals(errors, record['errors'])

    def test_regform_hidden_negative(self):
        """Form raises exception when trying to hide required field"""
        with self.assertRaises(ValueError):
            RegistrationForm(['email'])

    def test_regform_creation_positive(self):
        form = RegistrationForm(['position', 'company'])
        self.assertIsNone(form.position)
        self.assertIsNone(form.company)
