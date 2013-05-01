# -*- coding: utf-8 -*-
import os
from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from dirtyfields import DirtyFieldsMixin

from .settings import STORAGE, QUEUED_STORAGE_TASK
from .fields import LargeImageField

if QUEUED_STORAGE_TASK:
    IMAGE_STORAGE = STORAGE(task=QUEUED_STORAGE_TASK)
else:
    IMAGE_STORAGE = STORAGE()


def slug_upload_to(instance, filename):
    """
    return the slug of the image
    """
    from django.template.defaultfilters import slugify
    if instance.slug:
        return 'loupe/%s/%s' % (instance.slug, filename)
    elif instance.name:
        return'loupe/%s/%s' % (slugify(instance.name), filename)
    return 'loupe/%s/%s' % (os.path.splitext(filename)[0], filename)


class BaseLoupeImage(DirtyFieldsMixin, models.Model):
    name = models.CharField(_('name'), max_length=255)
    slug = models.CharField(_('slug'), max_length=255)
    description = models.TextField(_('description'), blank=True, null=True)
    image = LargeImageField(_('image'),
        storage=IMAGE_STORAGE,
        upload_to=slug_upload_to,
        blank=True, null=True,
        help_text=_('We will create an host the tileset form this image.'), )
    external_tileset_url = models.URLField(_('external tileset URL'),
        blank=True, null=True,
        help_text=_('The tileset for this image is hosted elsewhere.'))
    external_tileset_type = models.CharField(_('external tileset type'),
        blank=True, null=True,
        max_length=20,
        choices=(
            ('dzi', 'Deep Zoom (DZI)'),
            ('iif', 'International Image Interchage Format (IIF)'),
            ('lip', 'Legacy Image Pyramid'),
            ('osm', 'Open Street Maps (OSM)'),
            ('tms', 'Tiled Map Service (TMS)'),
            ('zoomify', 'Zoomify'),
        ), )
    image_height = models.IntegerField(_('image height'),
        blank=True, null=True,
        editable=False)
    image_width = models.IntegerField(_('image width'),
        blank=True, null=True,
        editable=False)
    tile_size = models.IntegerField(_('tile site'),
        default=256,
        blank=True, null=True,
        editable=False)
    base_tile_url = models.CharField(_('base tile URL'),
        max_length=255,
        blank=True, null=True,
        editable=False)
    thumbnail = models.FileField(_('thumbnail'), upload_to="loupe_thumbs", blank=True, null=True)
    document_name = models.CharField(_('document name'),
        max_length=255,
        blank=True, null=True,
        help_text=_('If this image is part of a document, enter its name here. Make sure all parts of this document have the same "document name".'))
    document_order = models.IntegerField(_('document order'),
        blank=True, null=True,
        help_text=_('The order in which this image appears in the document.'))

    @property
    def tileset_url(self):
        """
        Return the appropriate url for this object's tiles
        """
        if self.image:
            return "'%s.dzi'" % os.path.splitext(self.image.url)[0]
        else:
            return self.external_tileset_url

    @property
    def tileset_source(self):
        if self.external_tileset_type == 'zoomify':
            return """{width: %s, height: %s, tilesUrl: "%s", type: "zoomify"}""" % (self.image_width, self.image_height, self.external_tileset_url)
        else:
            return self.tileset_url

    class Meta:
        abstract = True

    def render(self):
        """
        return the rendered template to display this item in a webpage
        """
        from django.utils.safestring import mark_safe
        from django.template.loader import render_to_string
        base_template_name = "%s/%s_%%s.html" % (
            self._meta.app_label, self.__class__.__name__.lower())
        template_selection = [base_template_name % 'default', ]
        if self.external_tileset_url:
            template_selection.insert(0, base_template_name % self.external_tileset_type)
        return mark_safe(render_to_string(template_selection, {'object': self}))

    def clean(self):
        """
        Make sure either the image field is set or the external fields are set
        """
        from django.core.exceptions import ValidationError

        if self.image and self.external_tileset_url:
            raise ValidationError(_("Use either an uploaded image or an external tileset url."))
        elif not self.image and not self.external_tileset_url:
            raise ValidationError(_("Use either an uploaded image or an external tileset url."))
        elif self.external_tileset_url and not self.external_tileset_type:
            raise ValidationError(_("Please select an external tileset type when using an external tileset."))

    def update_metadata(self):
        """
        Update the tileset's metadata fields by getting the URL and parsing it
        """
        import tileset
        if self.external_tileset_type:
            tile_type = self.external_tileset_type
        else:
            tile_type = 'local'
        try:
            metadata_func = getattr(tileset, 'get_%s_metadata' % tile_type)
            metadata = metadata_func(self.tileset_url)

            self.image_height = metadata.get('height')
            self.image_width = metadata.get('width')
            self.tile_size = metadata.get('tilesize')
            self.base_tile_url = metadata.get('base_tile_url')
            self.save()
        except AttributeError:
            pass

    def save(self, *args, **kwargs):
        """
        Update the metadata if the imageurl changes
        """
        update_metadata = (
            "image" in self.dirty_fields or
            "external_tileset_type" in self.dirty_fields or
            "external_tileset_url" in self.dirty_fields)
        super(BaseLoupeImage, self).save(*args, **kwargs)
        if update_metadata:
            self.update_metadata()

    def __unicode__(self):
        return self.name


class LoupeImage(BaseLoupeImage):
    class Meta:
        verbose_name = _('Loupe Image')
        verbose_name_plural = _('Loupe Images')

    def get_absolute_url(self):
        return reverse('loupeimage-detail', kwargs={'slug': self.slug})


from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=LoupeImage)
def create_external_thumbnail(sender, instance, created, raw, using, *args, **kwargs):
    if instance.external_tileset_url and not hasattr(instance.thumbnail, 'file'):
        try:
            import tileset

            thumbnail_func = getattr(tileset, 'create_%s_thumbnail' % instance.external_tileset_type)
            filename, size, content = thumbnail_func(instance.tileset_url)
            instance.thumbnail.save(filename, content)
        except AttributeError:
            pass
