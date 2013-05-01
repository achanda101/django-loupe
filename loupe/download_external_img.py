import urllib
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
from PIL import Image

from django.core.files.base import ContentFile


def guess_image_format(content_type=''):
    """
    Try to figure out the image format from either the file name or content type
    """
    if content_type:
        parts = content_type.split('/')
        if parts[0] == 'image':
            return parts[1].upper()
    return None


def django_website_image(url):
    """
    Returns a filename, (width, height), ContentFile tuple for saving in a field

    filename, dimensions, contentfile = django_website_image(self.url)
    self.key_image.save(filename, contentfile)
    """
    import os
    from urlparse import urlparse
    url_filename = os.path.basename(urlparse(url).path)
    filepath, info = urllib.urlretrieve(url)
    img_format = guess_image_format(info.get('content-type', ''))
    image = Image.open(filepath)
    if image.mode not in ('L', 'RGB'):
        image = image.convert('RGB')

    destination = StringIO()
    image.save(destination, format=img_format)
    destination.seek(0)

    return (url_filename, image.size, ContentFile(destination.read()))
