import logging

from json import dumps as json_dumps

from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.encoders import encode_noop

from cherrypy import HTTPError

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
    # TODO: implement exponential backoff
    # https://developers.google.com/drive/v2/web/manage-uploads#exp-backoff

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

        # Send it to drive
        gd_rsrc = pub('google-api').post(
            'https://www.googleapis.com/upload/drive/v2/files'
            '?uploadType=multipart&convert=true',
            data=msg.as_string(),
            headers=dict(msg.items()))

        return gd_rsrc.json()
    except KeyError as ae:
        logger.debug('Error sending to drive: {} {} ({})'.format(
            gd_rsrc.status, gd_rsrc.reason, msg))
        raise HTTPError(500,
                        {'message': gd_rsrc.status, 'data': msg}) from ae
    except Exception as e:
        raise HTTPError(500) from e
