import re


def email(field, value, error):
    regex = r'^[a-zA-Z0-9_.+-]+@(?P<hostname>[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)$'
    match = re.match(regex, value)
    if not match:
        error(field, 'Invalid email address')
    else:
        hostname = match.group('hostname')
        for section in hostname.split('.'):
            if not section:
                error(field, 'Invalid email address')


def url(field, value, error):
    regex = (
        r'^(http(?:s)?\:\/\/[a-zA-Z0-9]+(?:(?:\.|\-)[a-zA-Z0-9]+)+'
        '(?:\:\d+)?(?:\/[\w\-]+)*(?:\/?|\/\w+\.[a-zA-Z]{2,4}'
        '(?:\?[\w]+\=[\w\-]+)?)?(?:\&[\w]+\=[\w\-]+)*)$'
    )
    if not re.match(regex, value):
        error(field, 'Invalid URL')
