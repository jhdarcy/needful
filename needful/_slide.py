# Standard module imports
from pathlib import Path
from secrets import token_hex
from typing import Optional, Union

# From this module
from ._css import CSSTheme
from ._slide_mixins import images, textboxes, plots
from ._preview import preview_slide
from ._utils import check_type


class Slide(images.ImageMixin, plots.PlotMixin, textboxes.TextboxMixin):
    """Represents a slide in the HTML presentation.

    Parameters
    ----------
    title : str
        The title of this slide. Can be set to an empty string if the slide does not require a title.
    columns : int
        The number of CSS grid columns in the slide.
    menu_title : str, optional
        A version of the title to display in the presentation's hidden navigation menu. Leave as `None` to set the
        menu title to `title`.
    theme : needful.CSSTheme, optional
        The CSS theme object to apply to this slide. Defaults to `None`. If `None`, this slide will use the styling
        defined in the CSS file for the whole presentation.
    page_number : bool, optional
        Whether to display the page number on this slide. If specified, this will override the `page_numbers` option
        set for the overall presentation.
    navigation_menu : bool, optional
        Whether to display the hidden navigation menu when the mouse hovers over the page number. If specified, this
        will override the `navigation_menu` option set for the overall presentation.
    autoscale : bool, optional
        Whether to automatically scale the slide up/down to best fit the window. If specified, this will override the
        `autoscale` option set for the overall presentation.
    allow_overflow : bool, optional
        Whether slide contents are allowed to overflow beyond the presentation window. If set to `True`, slide contents
        can extend beyond the bounds of the window, and normal browser scrolling is permitted. If `False`, content
        extending beyond the presentation window will be cut off. Only applies when `autoscale = True` (either for this
        slide or the overall presentation).
    disable_mathjax : bool, default=False
        Disables MathJax typesetting on this slide. Defaults to `False`. This setting only has an effect if
        `mathjax = True` is set for the overall presentation.
    id : str, optional
        The ID to give this slide. This is reserved for future functionality.
    """

    @property
    def html(self):
        # Stitch together HTML string.
        return "\n".join([str(element) for element in self._elements])

    def __init__(self,
                 title: str,
                 columns: int,
                 menu_title: Optional[str] = None,
                 theme: Optional[CSSTheme] = None,
                 page_number: Optional[bool] = None,
                 navigation_menu: Optional[bool] = None,
                 autoscale: Optional[bool] = None,
                 allow_overflow: Optional[bool] = None,
                 disable_mathjax: bool = False,
                 id: Optional[str] = None
                 ):

        # Assign slide ID, generate one randomly if not specified.
        check_type("id", id, Optional[str])
        if id is None or id.strip() == "":
            self.id = token_hex(5)
        else:
            self.id = id

        check_type("title", title, str)
        self.title = title

        check_type("columns", columns, int)
        if columns < 1:
            raise ValueError(f"columns = {columns}. Number of columns must be at least 1 or more.")
        self.n_cols = columns

        # Set menu title, raise error if both menu_title and title are blank.
        check_type("menu_title", menu_title, Optional[str])
        if menu_title is None:
            menu_title = ""
        if title.strip() == menu_title.strip() == "":
            raise ValueError("Slide title and menu title are blank. If the title is to be left blank, then menu_title needs to be set.")
        if menu_title.strip() == "":
            self.menu_title = title
        else:
            self.menu_title = menu_title

        check_type("theme", theme, Optional[CSSTheme])
        self.theme = theme
        self.theme_id = theme.id if theme is not None else None

        check_type("page_number", page_number, Optional[bool])
        self._page_number = page_number

        check_type("navigation_menu", navigation_menu, Optional[bool])
        self._nav_menu = navigation_menu

        check_type("autoscale", autoscale, Optional[bool])
        self._autoscale = autoscale

        check_type("allow_overflow", allow_overflow, Optional[bool])
        self._overflow = allow_overflow

        check_type("disable_mathjax", disable_mathjax, bool)
        self._disable_mathjax = disable_mathjax

        # Set menu title, raise error if both menu_title and title are blank.
        check_type("menu_title", menu_title, Optional[str])
        if menu_title is None:
            menu_title = ""
        if title.strip() == menu_title.strip() == "":
            raise ValueError("Slide title and menu title are blank. If the title is to be left blank, then menu_title needs to be set.")
        if menu_title.strip() == "":
            self.menu_title = title
        else:
            self.menu_title = menu_title

        self._elements = []
        # An array to track filled positions on the CSS grid.
        self._filled_pos = []

    def __repr__(self):
        title = {self.menu_title} if self.title.strip() == "" else self.title
        return f"<{title}, {self.n_plots} plots>"

    def _check_grid_pos(self, row: int, column: int) -> None:
        if (row, column) in self._filled_pos:
            raise ValueError(f"An element is already present in row {row}, column {column} of this slide!")
        else:
            self._filled_pos.append((row, column))

    def preview(self, css_file: Optional[Union[str, Path]] = None):
        """Creates and opens a preview of the slide.

        Parameters
        ----------
        css_file : str, Path, optional
            The .css file controlling the overall styling of this presentation. If left blank, the presentation will use
            the default needful style.
        """
        check_type("css_file", css_file, Optional[Union[str, Path]])

        # Nothing else to do except pass self to preview_slide(...) function.
        preview_slide(self, css_file)



