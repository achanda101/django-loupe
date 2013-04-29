#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django import template

register = template.Library()


@register.inclusion_tag("loupe/openseadragon_js.html", takes_context=True)
def openseadragon_js(context):
    from django.conf import settings
    context['DEBUG'] = settings.DEBUG
    return context
