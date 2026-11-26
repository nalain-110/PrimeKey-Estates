"""Cloudinary helpers for persistent property image storage."""
import os
import re
import uuid
from urllib.parse import urlsplit
from werkzeug.utils import secure_filename

import cloudinary
import cloudinary.uploader

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def is_allowed(filename):
    return bool(filename and '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS)


def _configure():
    required = ('CLOUDINARY_CLOUD_NAME', 'CLOUDINARY_API_KEY', 'CLOUDINARY_API_SECRET')
    missing = [name for name in required if not os.environ.get(name)]
    if missing:
        raise RuntimeError('Missing Cloudinary environment variables: ' + ', '.join(missing))
    cloudinary.config(
        cloud_name=os.environ['CLOUDINARY_CLOUD_NAME'],
        api_key=os.environ['CLOUDINARY_API_KEY'],
        api_secret=os.environ['CLOUDINARY_API_SECRET'],
        secure=True,
    )


def upload_image(file_storage, folder='primekey/properties'):
    """Upload remotely, falling back to the app's persistent local upload folder."""
    if not file_storage or not is_allowed(getattr(file_storage, 'filename', '')):
        return None
    try:
        _configure()
        file_storage.stream.seek(0)
        result = cloudinary.uploader.upload(
            file_storage.stream,
            folder=folder,
            resource_type='image',
            transformation={'width': 1600, 'crop': 'limit', 'quality': 'auto'},
        )
        image_url = result.get('secure_url')
        if image_url:
            return image_url
        raise RuntimeError('Cloudinary did not return an image URL')
    except Exception as exc:
        from flask import current_app
        current_app.logger.warning('Cloudinary upload failed; saving image locally: %s', exc)
        try:
            filename = secure_filename(file_storage.filename or '')
            extension = filename.rsplit('.', 1)[-1].lower()
            filename = f'{uuid.uuid4().hex}.{extension}'
            upload_folder = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_folder, exist_ok=True)
            file_storage.stream.seek(0)
            file_storage.save(os.path.join(upload_folder, filename))
            return filename
        except Exception:
            current_app.logger.exception('Local property image save failed')
            return None


def delete_image(value):
    """Delete a Cloudinary image URL; return False if it is not a Cloudinary URL."""
    if not value or 'res.cloudinary.com' not in str(value):
        return False
    try:
        _configure()
        path = urlsplit(str(value)).path
        marker = '/image/upload/'
        if marker not in path:
            return False
        public_path = path.split(marker, 1)[1].split('/')
        if public_path and re.fullmatch(r'v\d+', public_path[0]):
            public_path.pop(0)
        # Ignore optional delivery transformations before the asset path.
        if public_path and (',' in public_path[0] or public_path[0].startswith(('c_', 'f_', 'q_', 'w_', 'h_', 'e_'))):
            public_path.pop(0)
        public_id = '/'.join(public_path)
        public_id = re.sub(r'\.[^.]+$', '', public_id)
        if public_id:
            cloudinary.uploader.destroy(public_id, resource_type='image')
            return True
    except Exception as exc:
        print('Cloudinary deletion failed:', exc)
    return False


def image_src(value, default=None):
    """Return remote URLs as-is and serve legacy local filenames from static uploads."""
    if not value:
        return default
    value = str(value)
    if value.startswith(('http://', 'https://')):
        return value
    from flask import url_for
    return url_for('static', filename='images/uploads/' + value.lstrip('/'))
