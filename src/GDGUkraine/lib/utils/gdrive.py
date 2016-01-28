import logging
import random
import time

from json import dumps as json_dumps

from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.encoders import encode_noop

from cherrypy import HTTPError
import requests.exceptions

from .signals import pub


logger = logging.getLogger(__name__)


def gdrive_upload(filename, mime_type, fileobj):
    """
    Function: gdrive_upload
    Summary: Uploads given fileobj of mime_type
             to Google Drive, titling it filename
    Examples:
        gd_resp = gdrive_upload(file_name,
                                file_mime,
                                gen_participants_xlsx(part_data).getvalue())
    Attributes:
        @param (filename):str
        @param (mime_type):str
        @param (fileobj):bytes-like object
    Returns: JSON response from Google Drive API
    """

    # Alternative way:
    # https://developers.google.com/drive/v2/web/savetodrive

    # Btw, there's another alternative way, this button downloads file
    # to the user's browser and uploads it to Google Drive then:
    # https://developers.google.com/drive/v2/web/savetodrive

    try:
        msg = MIMEMultipart('related')

        # Add file metadata
        msg.attach(MIMEApplication(
            json_dumps({
                'title': filename,
                'mimeType': mime_type}),
            'json',
            _encoder=encode_noop))

        # Add file itself
        msg.attach(MIMEApplication(
            fileobj,
            mime_type))

        google_api = pub('google-api')

        # Send file to drive with exponential backoff enabled:
        # https://developers.google.com/drive/v2/web/manage-uploads#exp-backoff
        retries_count = 0
        while True:
            try:
                gd_rsrc = google_api.post(
                    'https://www.googleapis.com/upload/drive/v2/files'
                    '?uploadType=multipart&convert=true',
                    data=msg.as_string(),
                    headers=dict(msg.items()))
                break
            except requests.exceptions.HTTPError as http_error:
                if gd_rsrc.status < 500 or retries_count > 16:
                    raise http_error

                # Wait exponential time and then retry
                time.sleep(pow(2, retries_count) + random.random())
                retries_count += 1

        return gd_rsrc.json()
    except Exception as e:
        raise HTTPError(500) from e
        logger.error('Error sending to drive: {} {} ({})'.format(
            gd_rsrc.status, gd_rsrc.reason, msg))
        raise HTTPError(500,
                        {'message': gd_rsrc.status, 'data': msg}) from e
