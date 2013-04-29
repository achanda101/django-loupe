About
=====

Django Loupe provides an easy way to display zoomable, large images. The images may be hosted locally by uploading the original large image, or externally. Externally hosted images are referenced by their URL.

Zoomable images are displayed by making a tiled `image pyramid`_. There are several methods and formats for making this pyramids. Django Loupe creates locally-hosted tiles in the Deep Zoom format developed by Microsoft using the open source VIPS_ library.

The OpenSeadragon_ JavaScript library displays the locally- or externally-hosted images.


Install
=======

1. Install Django Loupe using ``pip``::

    pip install django-loupe

2. Add ``"loupe",`` to your Django project's ``INSTALLED_APPS``.

3. Install VIPS_ on your platform. There are packages for Windows, and most Linux distributions include a package. There is a homebrew recipe for Mac OS X.


Upload an image
===============

1. Add a new loupe image

2. Enter in a title and description

3. Click on the upload file button and select a high-res file

4. Save.


Enter an externally hosted image
================================

1. Add a new loupe image

2. Enter a title and description

3. Enter in the URL for the tiles. This is not the URL for the page where you view the image. You will have to look at the page source to discover the tileset URL. Different formats have standard description files and Django Loupe will determine the correct URL from these.

   * **Deep Zoom:** ``http://example.com/path/to/image/imagename.dzi``
   * **International Image Interoperability Framework:** ``http://example.com/path/to/image/info.xml``
   * **Zoomify:** ``http://example.com/path/to/image/ImageProperties.xml``

4. Select the type of External tileset type from the selection.

5. Save.


Serving an image
================

1. In the template include the JavaScript:

   .. code-block:: django

       {% load loupe_tags %}{% openseadragon_js %}

2. ``{{ object.render }}`` will include the HTML fragment for the large image.

   * If it is an external tile set, it looks for ``<modulename>/<classname>_<tileset_type>.html`` where ``<tileset_type>`` is the short name of the tileset type choice.
   * Finally, it looks in ``<modulename>/<classname>_default.html``



Using remote storage
====================

#. Use ``django-queued-storage``
#. Set ``'IMAGE_STORAGE'`` to appropriate storage type.
#. Specify setting ``'QUEUED_STORAGE_TASK'`` to either ``'loupe.task.TileAndTransfer'`` or ``'loupe.task.TileTransferAndDelete'``.


.. _`image pyramid`: http://msdn.microsoft.com/en-us/library/cc645077(v=vs.95).aspx
.. _VIPS: http://www.vips.ecs.soton.ac.uk/index.php?title=VIPS
.. _OpenSeadragon: http://openseadragon.github.io/
