# -*- coding: utf-8 -*-
from django.views.generic import DetailView
from .models import LoupeImage


class LoupeImageDetailView(DetailView):
    model = LoupeImage
