"""Module containing simple classes that represent the basic elements of slides in **needful** presentations: text boxes,
images, Plotly figures, etc.

These classes are not designed to be interacted with directly by the user, and are instead instantiated when the user
calls the various `Slide.add_textbox(...)`, `Slide.add_plot(...)`, etc. functions.
"""

from needful._html_objects.grid_object import GridObject
from needful._html_objects.plotly_figure import PlotlyFigure
from needful._html_objects.textbox import TextBox
from needful._html_objects.image import Image
