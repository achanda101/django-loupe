# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.files.storage import get_storage_class


DEFAULT_SETTINGS = {
    'IMAGE_STORAGE': 'loupe.storage.FileSystemTilesetStorage',
    'QUEUED_STORAGE_TASK': '',
    'THUMB_SIZE': 200,
}

USER_SETTINGS = DEFAULT_SETTINGS.copy()
USER_SETTINGS.update(getattr(settings, 'LOUPE_SETTINGS', {}))
USER_SETTINGS['STORAGE'] = get_storage_class(USER_SETTINGS['IMAGE_STORAGE'])

globals().update(USER_SETTINGS)

HAS_CELERY = 'celery' in settings.INSTALLED_APPS
