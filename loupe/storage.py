from django.core.files.storage import Storage, FileSystemStorage

from .tileset import create_tileset, create_thumbnail


class TilesetStorage(Storage):
    def save(self, name, content):
        """
        Save the image and then create the tileset and a thumbnail
        """
        filename = super(TilesetStorage, self).save(name, content)
        create_tileset(self.path(filename))
        create_thumbnail(self.path(filename))
        return filename


class FileSystemTilesetStorage(TilesetStorage, FileSystemStorage):
    pass
