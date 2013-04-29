#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url

from .views import LoupeImageDetailView

urlpatterns = patterns('',
    url(r'^(?P<slug>[-_\w]+)/$',
        LoupeImageDetailView.as_view(),
        name='loupeimage-detail'),
)
