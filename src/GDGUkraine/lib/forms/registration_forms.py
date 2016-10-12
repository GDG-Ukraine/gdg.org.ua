import logging

from wtforms.form import Form
from wtforms.fields import (
    StringField, TextAreaField, SelectField,
    BooleanField, SelectMultipleField,
)
from wtforms.widgets import ListWidget, RadioInput, CheckboxInput
from wtforms.validators import Required, Length, Email, URL, Optional

from GDGUkraine.model import (
    EXPERIENCE_CHOICES, ENGLISH_CHOICES,
    GENDER_CHOICES, TSHIRT_CHOICES,
)

from .widgets import InlineWidget


logger = logging.getLogger(__name__)


class RegistrationForm(Form):

    name = StringField(
        label='Name',
        validators=[
            Required(),
            Length(max=35),
        ],
        render_kw={
            'placeholder': 'e.g. Sergey',
        },
    )
    surname = StringField(
        label='Surname',
        validators=[
            Required(),
            Length(max=35),
        ],
        render_kw={
            'placeholder': 'e.g. Brin',
        },
    )
    nickname = StringField(
        label='Nickname',
        validators=[
            Length(max=45),
        ],
        render_kw={
            'placeholder': 'e.g. SuperBrin',
        },
    )
    email = StringField(
        label='Email',
        validators=[
            Required(),
            Email(),
        ],
        render_kw={
            'placeholder': 'anything@example.com',
        },
    )
    phone = StringField(
        label='Phone number',
        validators=[
            Length(max=20),
        ],
        render_kw={
            'placeholder': '0931234567',
        },
    )
    gplus = StringField(
        label='Google+ id',
        validators=[
            Required(),
        ],
        render_kw={
            'placeholder': 'e.g. 1000000000042',
        },
    )
    www = StringField(
        label='Website URL',
        validators=[
            Optional(),
            Length(max=100),
            URL(),
        ],
        render_kw={
            'placeholder': 'Start with http://',
        },
    )
    hometown = StringField(
        label='City',
        validators=[
            Required(),
            Length(max=30),
        ],
        render_kw={
            'placeholder': 'e.g. Mountain View',
        },
    )
    company = StringField(
        label='Company',
        validators=[
            Length(max=64),
        ],
        render_kw={
            'placeholder': 'e.g. Google',
        },
    )
    position = StringField(
        label='Position',
        validators=[
            Length(max=64),
        ],
        render_kw={
            'placeholder': 'e.g. Cofounder',
        },
    )
    experience_level = SelectField(
        label='Experience level',
        choices=[(c, c.capitalize()) for c in EXPERIENCE_CHOICES],
    )
    experience_desc = TextAreaField(
        label='Experience description',
        render_kw={
            'placeholder': (
                'e.g. Software developer particularly interested in Java '
                'technologies and Google applications. Worked in various '
                'countries: Ukraine, USA, Poland. '
                'Have great ability to work remotely, high mobility, '
                'sense of humor.'
            ),
        },
    )
    interests = TextAreaField(
        label='Interests',
        render_kw={
            'placeholder': 'e.g. Google, Android, Chrome',
        },
    )
    events_visited = StringField(
        label='Events visited',
        render_kw={
            'placeholder': (
                'e.g. IO Extended 2015, GDG DevFest, hackathons, '
                'code labs, Study Jams or WTM events'
            ),
        },
    )
    english_knowledge = SelectField(
        label='English knowledge',
        choices=[(c, c.capitalize()) for c in ENGLISH_CHOICES],
    )
    t_shirt_size = SelectField(
        label='T-Shirt size',
        choices=[(c.lower(), c) for c in TSHIRT_CHOICES],
    )
    gender = SelectField(
        label='Gender',
        choices=[(c, c.capitalize()) for c in GENDER_CHOICES],
        validators=[Required()],
        widget=InlineWidget(prefix_label=False),
        option_widget=RadioInput(),
    )
    additional_info = TextAreaField(
        label='Comments',
        render_kw={
            'placeholder': 'If you have something to say us, leave it here =)',
        },
    )

    def __init__(self, hidden=None, *args, **kwargs):
        if hidden is None:
            hidden = []

        super(RegistrationForm, self).__init__(*args, **kwargs)

        for name in hidden:
            field = getattr(self, name, None)
            if field and field.flags.required:
                # Hiding required field might cause db operational error
                # Hence do not allow hiding required fields
                logger.error('Trying to hide required field %s', name)
                raise ValueError('Field {} is required'.format(name))
            delattr(self, name)


def get_additional_fields_form_cls(definitions):
    if definitions is None:
        definitions = []

    class AdditionalFieldsForm(Form):
        pass

    for definition in definitions:
        field = _create_field(definition)
        setattr(AdditionalFieldsForm, definition['name'], field)

    return AdditionalFieldsForm


def _create_field(definition):
    type_ = definition['type']
    factory = globals().get('_make_{}'.format(type_))
    if factory is None:
        logger.error('Unknown field type: {}'.format(type_))
        return None
    return factory(definition)


def _make_select(definition):
    assert definition['type'] == 'select', definition['type']
    custom = definition.get('allow_custom', False)
    multiple = definition.get('multiple', False)
    options = {}
    field_cls = SelectField

    if multiple:
        options['widget'] = ListWidget
        options['option_widget'] = CheckboxInput
        field_cls = SelectMultipleField

    if custom:
        logger.warn('select field with custom choice is not supported yet')

        class CustomSelectField(field_cls):
            pass

        # workaround to make select with custom pass the validation
        def pre_validate_multiple(self, form):
            if self.data:
                values = list(c[0] for c in self.choices)
                custom_counter = 0
                for d in self.data:
                    if d not in values:
                        custom_counter += 1
                        if custom_counter > 1:
                            # Allow only one custom choice
                            raise ValueError(self.gettext(
                                "'%(value)s' is not a valid choice "
                                'for this field' % dict(value=d)
                            ))

        def pre_validate_singe(self, form):
            # If it is a radio button list with custom values
            # then no validation is needed as any value is allowed
            pass

        CustomSelectField.pre_validate = (
            pre_validate_multiple if multiple else pre_validate_singe
        )

        field_cls = CustomSelectField

    field = field_cls(
        label=definition['title'],
        choices=[(c, c) for c in definition.get('options', [])],
        **options
    )

    return field


def _make_checkbox(definition):
    assert definition['type'] == 'checkbox', definition['type']
    return BooleanField(label=definition['title'])


def _make_text(definition):
    assert definition['type'] == 'text', definition['type']
    validators = None
    if definition.get('required', False):
        validators = [Required()]
    field = StringField(
        label=definition['title'],
        validators=validators,
    )
    return field
