"""Module containing simple classes that represent the basic elements of slides in **needful** presentations: text boxes,
images, Plotly figures, etc.

These classes are not designed to be interacted with directly by the user, and are instead instantiated when the user
calls the various `Slide.add_textbox(...)`, `Slide.add_plot(...)`, etc. functions.
"""
from .bokeh_figure import BokehFigure
from .image import Image
from .mpl_figure import MPLFigure
from .plotly_figure import PlotlyFigure
from .textbox import TextBox
