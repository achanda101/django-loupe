========================
Django Loupe v |version|
========================

About
=====

Django Loupe provides an easy way to display zoomable, large images. The images may be hosted locally by uploading the original large image, or externally. Externally hosted images are referenced by their URL.

Zoomable images are displayed by making a tiled `image pyramid`_. There are several methods and formats for making this pyramids. Django Loupe creates locally-hosted tiles in the Deep Zoom format developed by Microsoft using the open source VIPS_ library.

The OpenSeadragon_ JavaScript library displays the locally- or externally-hosted images.


.. _`image pyramid`: http://msdn.microsoft.com/en-us/library/cc645077(v=vs.95).aspx
.. _VIPS: http://www.vips.ecs.soton.ac.uk/index.php?title=VIPS
.. _OpenSeadragon: http://openseadragon.github.io/



Contents
========

.. toctree::
   :maxdepth: 2
   :glob:

   getting_started
   reference/index
