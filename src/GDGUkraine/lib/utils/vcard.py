import binascii
import os
import urllib

from Crypto import Random
from Crypto.Cipher import AES

from .url import base_url, url_for_class

# TODO: make this stuff normal
card_secret_key = os.getenv('CARD_SECRET_KEY',
                            'sHsagghsSBackFbscoEhTdBtpQtsszds').encode('utf8')


def pad(s):
    assert isinstance(s, bytes)
    return s + b'\0' * (AES.block_size - len(s) % AES.block_size)


def aes_decrypt(ciphertext):
    if not isinstance(ciphertext, (str, bytes)):
        ciphertext = str(ciphertext)
    if not isinstance(ciphertext, bytes):
        ciphertext = ciphertext.encode('ascii')
    ciphertext = binascii.unhexlify(ciphertext)
    iv = ciphertext[:AES.block_size]
    cipher = AES.new(card_secret_key, AES.MODE_CBC, iv)
    plaintext = cipher.decrypt(ciphertext[AES.block_size:])
    return plaintext.rstrip(b'\0').decode('utf8')


def aes_encrypt(message):
    if not isinstance(message, (str, bytes)):
        message = str(message)
    if not isinstance(message, bytes):
        message = message.encode('utf8')
    message = pad(message)
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(card_secret_key, AES.MODE_CBC, iv)
    return binascii.hexlify(iv + cipher.encrypt(message)).decode('ascii')


def make_vcard(user_reg, url=None):
    if url is None:
        url = url_for_class('controller.Root.card', [aes_encrypt(user_reg.id)])

    if not url.startswith('http'):
        url = ('' if url.startswith('/') else '/').join([base_url(), url])

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
