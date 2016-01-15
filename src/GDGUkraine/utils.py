import base64
import json
import logging
import os
import binascii
import urllib
import inspect

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import cherrypy as cp

from blueberrypy.template_engine import get_template

import html2text

from Crypto import Random
from Crypto.Cipher import AES

import routes


logger = logging.getLogger(__name__)

# TODO: make this stuff normal
card_secret_key = os.getenv('CARD_SECRET_KEY',
                            'sHsagghsSBackFbscoEhTdBtpQtsszds').encode('utf8')
url_resolve_map = None


def is_admin():
    return isinstance(cp.session.get('admin_user'), dict) and \
        isinstance(cp.session.get('google_oauth'), dict) and \
        isinstance(cp.session.get('google_user'), dict)


def gmail_send(oauth2session, message, sbj, to_email,
               from_email='GDG Team Robot <kyiv@gdg.org.ua>'):

    message['to'] = to_email
    message['from'] = from_email
    message['subject'] = sbj

    st = oauth2session.post(
        'https://www.googleapis.com/gmail/v1/users/{userId}/messages/send'
        .format(userId='me'),
        data=json.dumps({'raw': base64.urlsafe_b64encode(message.as_string()
                                                         .encode('utf8'))
                        .decode('utf8')}),
        headers={"content-type": "application/json"})

    logger.debug(st.json())
    logger.debug('Sent message to {}'.format(to_email))
    return st.json()


def gmail_send_html(oauth2session, template, payload, **kwargs):

    assert isinstance(payload, dict), 'gmail_send_html only accepts dict'

    msg = MIMEMultipart('alternative')

    html_payload = get_template(template).render(**payload)

    plain_text_payload = html2text.html2text(html_payload)

    msg.attach(MIMEText(plain_text_payload, 'plain'))
    msg.attach(MIMEText(html_payload, 'html'))

    return gmail_send(oauth2session, message=msg, **kwargs)


def gmail_send_text(oauth2session, payload, **kwargs):

    msg = MIMEText(payload)

    return gmail_send(oauth2session, message=msg, **kwargs)


def pad(s):
    return s + b'\0' * (AES.block_size - len(s) % AES.block_size)


def aes_encrypt(message):
    if isinstance(message, str):
        message = message.encode('utf8')
    message = pad(message)
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(card_secret_key, AES.MODE_CBC, iv)
    return binascii.hexlify(iv + cipher.encrypt(message)).decode('ascii')


def aes_decrypt(ciphertext):
    if isinstance(ciphertext, str):
        ciphertext = binascii.unhexlify(ciphertext.encode('ascii'))
    iv = ciphertext[:AES.block_size]
    cipher = AES.new(card_secret_key, AES.MODE_CBC, iv)
    plaintext = cipher.decrypt(ciphertext[AES.block_size:])
    return plaintext.rstrip(b'\0').decode('utf8')


def make_vcard(user_reg, url=None):
    if url is None:
        url = '/card/{}'.format(aes_encrypt(user_reg.user.id))

    if not url.startswith('http'):
        url = 'https://gdg.org.ua{}'.format(url)

    vcard = '''BEGIN:VCARD
VERSION:2.1
N:{user.name};{user.surname}
EMAIL;TYPE=INTERNET:{user.email}
NOTE:REG:{reg.id} EV:{event.id}
URL:{url}
END:VCARD'''
    return urllib.parse.quote_plus(
        vcard.format(
            user=user_reg.user, reg=user_reg, event=user_reg.event,
            url=url))


def build_url_map(force=False):
    '''Builds resolve map for class-based routes'''

    def retrieve_class_routes(cls, mp, handler_cls=None):
        if handler_cls is None:
            handler_cls = '.'.join([cls.__class__.__module__,
                                    cls.__class__.__name__]).lower()
        if not mp.endswith('/'):
            mp = '/'.join([mp, ''])
        res = {}
        for method in dir(cls):
            hndlr = getattr(cls, method)
            uri = mp
            if hasattr(hndlr, '__name__') \
                    and hndlr.__name__ != 'index' \
                    and method:
                uri = ''.join([mp, method])
            if not uri:
                uri = '/'

            if inspect.ismethod(hndlr):
                if getattr(hndlr, 'exposed', False):
                    if hndlr.__name__ != method:
                        continue
                    # That's it! It's a final method

                    # (args_, varargs_, varkw_, values_) = \
                    #     inspect.getargspec(hndlr)
                    # pprint(inspect.getargspec(hndlr))
                    # Use inspect.getargspec
                    # instead of inspect.signature for Python < 3.5
                    params = inspect.signature(hndlr).parameters

                    key_cls = handler_cls
                    if hndlr.__name__ != 'index':
                        key_cls = '.'.join([handler_cls, hndlr.__name__])

                    if res.get(key_cls):
                        continue

                    res[key_cls] = {
                        'args': params,
                        'url': (uri
                                if uri and uri.endswith('/')
                                else '/'.join([uri]))}
            elif not inspect.isfunction(hndlr) and \
                    not isinstance(hndlr, property) and \
                    not method.startswith('__'):
                # Looks like we have another class instance mounted and nested
                # import ipdb; ipdb.set_trace()
                res.update(
                    retrieve_class_routes(
                        cls=hndlr,
                        mp=(''
                            if uri.endswith('/')
                            else '/').join([uri, method]),
                        handler_cls='.'.join([handler_cls, method])))
        # TODO: handle `index` and `default` methods
        if res.get(handler_cls):
            res['.'.join([handler_cls, 'index'])] = res[handler_cls]
        return res

    global url_resolve_map
    urls = {'__routes__': {}}
    # urls = {'__routes__': []}
    if url_resolve_map is None or force:
        for script in cp.tree.apps:
            app = cp.tree.apps[script]
            request_dispatcher = app.config['/'].get('request.dispatch')
            if app.root is not None:
                print('It is class-based routed app')
                print(script, app)
                urls.update(retrieve_class_routes(app.root,
                                                  mp=app.script_name))
            elif isinstance(request_dispatcher,
                            cp._cpdispatch.RoutesDispatcher):
                print('It is Routes routed app')
                print('Skipping...')
                print(script, app, request_dispatcher)
                urls['__routes__'][app.script_name] = request_dispatcher
                # urls['__routes__'].append({'dispatcher': request_dispatcher,
                #                            'script_name': app.script_name})
        url_resolve_map = urls
        return urls
    else:
        return urls


def url_for(handler, type_='cherrypy', **url_params):
    '''handler=GDGUkraine.controller.Root'''

    if type_ == 'class-based':
        app_name = __name__.split('.')[0].lower()
        handler = handler.lower()

        if handler.split('.')[0] != app_name:
            handler = '.'.join([app_name, handler])

        url_route = url_resolve_map.get(handler)
        print(url_route)
        return cp.url(url_route['url'],
                      script_name='',
                      # script_name=url_resolve_map['script_name'],
                      base='https://gdg.org.ua')

    elif type_ == 'routes':
        script_name = '/api'  # How do we negotiate this?
        dispatcher = url_resolve_map['__routes__'].get(script_name)
        routes.request_config().mapper = dispatcher
        return cp.url(routes.url_for(handler),
                      script_name=url_resolve_map['script_name'],
                      base='https://gdg.org.ua')
    else:
        if not handler.startswith('/'):
            handler = '/'.join(['', handler])
        return cp.url(handler)
