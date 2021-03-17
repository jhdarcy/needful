"""Implements the Slide.preview() function, without circular dependencies."""
from pathlib import Path
from typing import Optional, Union


def preview_slide(slide, css_file: Optional[Union[str, Path]] = None):
    """Creates and opens a preview of the given slide.

    Note: this function is designed to be called from within `Slide.preview()`, but should work externally too.

    Parameters
    ----------
    slide: needful.Slide
        The slide object to preview.
    css_file : str, Path, optional
        The .css file controlling the overall styling of this presentation. If left blank, the presentation will use
        the default needful style.
    """
    from ._presentation import Presentation

    # Not much to do except create Presentation, add slide to it and save as "preview.html".
    pres = Presentation(slide.title, css_file=css_file)
    pres.add_slide(slide)
    pres.generate_html("preview.html", open_file=True)
