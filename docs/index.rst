.. needful documentation master file, created by
   sphinx-quickstart on Fri Mar 12 14:03:14 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

needful
=======

needful is a Python library for generating HTML presentations and dashboards. The resulting HTML file is entirely
self-contained, and can be easily shared or hosted online.

Overview
========

Creating a fully fledged needful presentation is very straightforward:

.. literalinclude:: py_examples/my_first_presentation.py
   :language: python

The resulting HTML file can be viewed `here <My\ First\ Presentation.html>`_.

This example demonstrates the overall pattern of use for needful:

#. Create one or more :py:class:`Slide` instances and add content in the form of textboxes, images or plots.
#. Add the slides to a :py:class:`Presentation` instance.
#. Output the final HTML file.

This example also demonstrates needful's support for `Markdown <https://www.markdownguide.org>`_ for simple
text formatting, and seamless embedding of `Plotly <https://plotly.com/python/>`_ charts.

For some more substantial demonstrations of Needful's capabilities, see the Examples section.

.. toctree::
   :maxdepth: 2
   :caption: Contents:


* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
