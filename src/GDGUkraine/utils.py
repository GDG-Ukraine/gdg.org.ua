import base64
import json
import logging
import os
import binascii

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import cherrypy as cp

from blueberrypy.template_engine import get_template

import html2text

from Crypto import Random
from Crypto.Cipher import AES


logger = logging.getLogger(__name__)

# TODO: make this stuff normal
card_secret_key = os.getenv('CARD_SECRET_KEY',
                            'sHsagghsSBackFbscoEhTdBtpQtsszds').encode('utf8')


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
