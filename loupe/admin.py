# -*- coding: utf-8 -*-
from django.contrib import admin

from .base_admin import BaseLoupeImageAdmin
from .models import LoupeImage

admin.site.register(LoupeImage, BaseLoupeImageAdmin)
