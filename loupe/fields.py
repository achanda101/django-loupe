# -*- coding: utf-8 -*-
from django.db.models.fields.files import FileField, FieldFile


class LargeImageFieldFile(FieldFile):
    def _thumbnail_url(self):
        import os
        self._require_file()
        image_url = self.storage.url(self.name)
        name, ext = os.path.splitext(image_url)
        return "{0}_thumb.jpg".format(name)
    thumbnail_url = property(_thumbnail_url)


class LargeImageField(FileField):
    """
    A field for handling some special characteristics of large images that
    are created into tilesets
    """
    attr_class = LargeImageFieldFile
