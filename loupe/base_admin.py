# -*- coding: utf-8 -*-
from django.contrib import admin
from django.conf import settings


class BaseLoupeImageAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('name', 'description', )
        }),
        ('Source', {
            'fields': ('image', 'thumbnail', 'external_tileset_url', 'external_tileset_type')
        }),
        ('Document Info', {
            'fields': ('document_name', 'document_order')
        }),
        ('Advanced', {
            'fields': ('slug', ),
            'classes': ('collapsed', )
        })
    )
    list_display = ('thumbnail_img', 'name', 'tileset_type', 'document', )
    prepopulated_fields = {"slug": ("name", )}

    def thumbnail_img(self, obj):
        """
        Show the thumbnail or the missing thumbnail_img
        """
        if hasattr(obj.thumbnail, 'file') and obj.thumbnail.file.url:
            url = obj.thumbnail.file.url
        elif hasattr(obj.image, 'file') and obj.image.thumbnail_url:
            url = obj.image.thumbnail_url
        else:
            url = "%s%s" % (settings.STATIC_URL, "loupe/noimgavailable.png")

        return '<img src="{0}" alt="{1}" />'.format(url, obj.name)
    thumbnail_img.short_description = "Thumbnail"
    thumbnail_img.allow_tags = True

    def tileset_type(self, obj):
        """
        Show the type of tileset
        """
        if obj.external_tileset_type:
            return "Externally hosted %s" % obj.get_external_tileset_type_display()
        else:
            return "Locally hosted DeepZoom"

    def document(self, obj):
        """
        Show the document information
        """
        if obj.document_name:
            return "{0} ({1})".format(obj.document_name, obj.document_order)
        else:
            return ""
