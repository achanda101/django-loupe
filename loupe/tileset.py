import os
import subprocess
import urllib
import re

WIDTH_RE = "width=[\"\'](\d+)[\"\']"
HEIGHT_RE = "height=[\"\'](\d+)[\"\']"
TILESIZE_RE = "tilesize=[\"\'](\d+)[\"\']"


def get_thumbnail_path(image_path):
    """
    Get the derived thumbnail path from the image_path
    """
    path, filename = os.path.split(image_path)
    name, ext = os.path.splitext(filename)
    return os.path.join(path, "%s_thumb.jpg" % name)


def create_tileset(image_path):
    """
    Create a tileset from an image
    """
    path, filename = os.path.split(image_path)
    name, ext = os.path.splitext(filename)
    dest_path = os.path.join(path, name)
    cmd = ['vips', 'dzsave', image_path, dest_path, '--suffix', ".jpg[Q=100]", ]
    return subprocess.call(cmd)


def get_tileset_files(image_path):
    """
    Return a list of all the files involved in the tileset for given image,
    including the original image
    """
    path, filename = os.path.split(image_path)
    file_list = []
    for dirpath, dirnames, filenames in os.walk(path):
        file_list.extend([os.path.join(dirpath, name) for name in filenames])
    return file_list


def create_thumbnail(image_path):
    from .settings import THUMB_SIZE
    dest_path = get_thumbnail_path(image_path)
    cmd = [
        'vipsthumbnail', image_path,
        '--output', dest_path,
        '--size', str(THUMB_SIZE)]
    return subprocess.call(cmd)


def get_data(url):
    filepath, info = urllib.urlretrieve(url)
    try:
        return open(filepath).read()
    except IOError:
        return ""


def extract_data(regex, string, flags=re.I):
    """
    Return the data from the regular expression
    """
    result = re.search(regex, string, flags)
    if result:
        return result.groups()
    else:
        return []


def get_dzi_metadata(url):
    """
    url should be in the format "http://domain.com/path/to/images.dzi"
    """
    dzi_data = get_data(url)
    width = extract_data(WIDTH_RE, dzi_data)
    height = extract_data(HEIGHT_RE, dzi_data)
    tilesize = extract_data(TILESIZE_RE, dzi_data)
    path, ext = os.path.splitext(url)
    output = {'base_tile_url': "%s_files/" % path}
    if width:
        output['width'] = int(width[0])
    if height:
        output['height'] = int(height[0])
    if tilesize:
        output['tilesize'] = int(tilesize[0])
    return output


def get_local_metadata(url):
    """
    For handling locally hosted images
    """
    from django.contrib.sites.models import Site
    url = "http://%s" % Site.objects.get_current().domain
    return get_dzi_metadata(url)


def create_zoomify_thumbnail(url):
    """
    Download the 0-0-0.jpg image to use as the thumbnail.
    Returns a filename, (width, height), ContentFile tuple for saving in a field
    """
    from .download_external_img import django_website_image
    thumb_url = url.replace('ImageProperties.xml', 'TileGroup0/0-0-0.jpg')
    name = "{0}.jpg".format(thumb_url.split("/")[-3])
    filename, size, contentfile = django_website_image(thumb_url)
    return name, size, contentfile


def get_zoomify_metadata(url):
    """
    url should be in the format "http://domain.com/path/to/images/ImageProperties.xml"
    """
    zoomify_data = get_dzi_metadata(url)
    zoomify_data['base_tile_url'] = url.replace('ImageProperties.xml', '')
    return zoomify_data
