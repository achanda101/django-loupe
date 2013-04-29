from queued_storage.task import Transfer, TransferAndDelete
from celery import task

try:
    from celery.utils.log import get_task_logger
except ImportError:
    from celery.log import get_task_logger

logger = get_task_logger(name=__name__)

from .tileset import create_tileset, get_tileset_files, create_thumbnail


@task
def create_tileset_async(image_path):
    """
    """
    create_tileset(image_path)
    create_thumbnail(image_path)


class TileAndTransfer(Transfer):
    """
    A :class:`~queued_storage.tasks.Transfer` subclass which creates a tileset
    from the file with the given name and transfers everything to the remote
    storage.
    """
    def transfer(self, name, local, remote, **kwargs):
        """
        Transfers the file with the given name from the local to the remote
        storage backend.

        :param name: The name of the file to transfer
        :param local: The local storage backend instance
        :param remote: The remote storage backend instance
        :returns: `True` when the transfer succeeded, `False` if not. Retries
                  the task when returning `False`
        :rtype: bool
        """
        if create_tileset(name) == 1:
            logger.error("Unable to create a tileset.")
        if create_thumbnail(name) == 1:
            logger.error("Unable to create a thumbnail.")
        for path in get_tileset_files(name):
            try:
                remote.save(path, local.open(path))
                return True
            except Exception as e:
                logger.error("Unable to save '%s' to remote storage. "
                             "About to retry." % path)
                logger.exception(e)
                return False


class TileTransferAndDelete(TileAndTransfer):
    """
    A :class:`~queued_storage.tasks.Transfer` subclass which creates a tileset
    from the file with the given name and transfers everything to the remote
    storage and deletes the local files when successful
    """
    def transfer(self, name, local, remote, **kwargs):
        result = super(TransferAndDelete, self).transfer(name, local,
                                                         remote, **kwargs)
        if result:
            local.delete(name)
        return result
