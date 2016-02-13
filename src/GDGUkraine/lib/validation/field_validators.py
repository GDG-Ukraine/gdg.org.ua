import re


def email(field, value, error):
    regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(regex, value):
        error(field, 'Not a valid email address')


def url(field, value, error):
    regex = (
        r'^(http(?:s)?\:\/\/[a-zA-Z0-9]+(?:(?:\.|\-)[a-zA-Z0-9]+)+'
        '(?:\:\d+)?(?:\/[\w\-]+)*(?:\/?|\/\w+\.[a-zA-Z]{2,4}'
        '(?:\?[\w]+\=[\w\-]+)?)?(?:\&[\w]+\=[\w\-]+)*)$'
    )
    if not re.match(regex, value):
        error(field, 'Not a valid URL')
