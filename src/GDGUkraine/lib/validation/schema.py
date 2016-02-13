from .field_validators import email, url


regform_schema = {
    'name': {
        'type': 'string',
        'maxlength': 35,
        'required': True,
    },
    'surname': {
        'type': 'string',
        'maxlength': 35,
        'required': True,
    },
    'nickname': {
        'type': 'string',
        'maxlength': 45,
    },
    'email': {
        'type': 'string',
        'required': True,
        'validator': email,
    },
    'phone': {
        'type': 'string',
        'nullable': True,
        'maxlength': 20,
    },
    'gplus': {
        'type': 'string',
        'required': True,
        'maxlength': 128,
    },
    'hometown': {
        'type': 'string',
        'nullable': True,
        'maxlength': 30,
    },
    'company': {
        'type': 'string',
        'nullable': True,
        'maxlength': 64,
    },
    'position': {
        'type': 'string',
        'nullable': True,
        'maxlength': 64,
    },
    'www': {
        'type': 'string',
        'nullable': True,
        'maxlength': 100,
        'validator': url,
    },
    'experience_level': {
        'allowed': [
            'newbie', 'elementary', 'intermediate',
            'advanced', 'jedi',
        ],
        'nullable': True,
    },
    'english_knowledge': {
        'allowed': [
            'elementary', 'intermediate', 'upper intermediate',
            'advanced', 'native',
        ],
    },
    't_shirt_size': {
        'allowed': [
            'xs', 'XS',
            's', 'S',
            'm', 'M',
            'l', 'L',
            'xl', 'XL',
            'xxl', 'XXL',
        ],
    },
    'gender': {
        'allowed': ['male', 'female', ],
    },
}
