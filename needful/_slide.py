# Standard module imports
from typing import Optional, Union
from pathlib import Path
from secrets import token_hex

# Third-party module imports
from plotly.graph_objects import Figure

# From this module
from ._css import CSSTheme
from ._html_objects import TextBox, Image, PlotlyFigure
from ._utils import check_type


class Slide:
    """Represents a slide in the HTML presentation.

    Parameters
    ----------
    title : str
        The title of this slide. Can be set to an empty string if the slide does not require a title.
    columns : int
        The number of CSS grid columns in the slide.
    theme : needful.CSSTheme, optional
        The CSS theme object to apply to this slide. Defaults to `None`. If `None`, this slide will use the styling
        defined in the CSS file for the whole presentation.
    page_number : bool, optional
        Whether to display the page number on this slide. If specified, this will override the `page_numbers` option
        set for the overall presentation.
    disable_mathjax : bool, default=False
        Disables MathJax typesetting on this slide. Defaults to `False`. (Note: this setting only has an effect if
        `mathjax = True` is set for the overall presentation.)
    menu_title : str, optional
        A version of the title to display in the presentation's hidden navigation menu. Leave as `None` to set the
        menu title to `title`.
    id : str, optional
        The ID to give this slide. This is reserved for future functionality.
    """

    @property
    def _plots(self):
        return [e for e in self._elements if type(e) == PlotlyFigure]

    @property
    def n_plots(self):
        return len(self._plots)

    @property
    def html(self):
        # Stitch together HTML string.
        return "\n".join([str(element) for element in self._elements])

    @property
    def plotly_func(self):
        if self.n_plots == 0:
            return "return"
        else:
            # Get list of Plotly JS strings, join them together to form this slide's 'plot' function:
            plotly_funcs = [plot.get_js() for plot in self._plots]
            return ";\n".join(plotly_funcs)

    @property
    def purge_func(self):
        if self.n_plots == 0:
            return "return"
        else:
            # Get figure IDs, construct all-important Plotly purge function.
            plot_ids = [plot.fig_id for plot in self._plots]
            return "\n".join([f'Plotly.purge("{plot_id}");' for plot_id in plot_ids])

    def __init__(self,
                 title: str,
                 columns: int,
                 theme: Optional[CSSTheme] = None,
                 page_number: Optional[bool] = None,
                 disable_mathjax: bool = False,
                 menu_title: Optional[str] = None,
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

        check_type("theme", theme, Optional[CSSTheme])
        self.theme = theme
        self.theme_id = theme.id if theme is not None else None

        check_type("page_number", page_number, Optional[bool])
        self.page_number = page_number

        check_type("disable_mathjax", disable_mathjax, bool)
        self.disable_mathjax = disable_mathjax

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

        self.n_tabs = 0
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

    def add_textbox(self, content: str, row: int, column: int, row_span: int = 1, col_span: int = 1,
                    markdown: bool = True, keep_linebreaks: bool = True) -> None:

        """Add a textbox to this slide, in the specified row and column.

        Parameters
        ----------
        content : str
            A string containing the text to add, which may include Markdown or HTML formatting. Use with `markdown
            = False` to ignore any possible Markdown formatting and use literal text and HTML.
        row : int
            The grid row in which to place this textbox.
        column : int
            The grid column in which to place this textbox.
        row_span : int
            The number of rows for this textbox to span (defaults to `1`).
        col_span : int
            The number of columns for this textbox to span (defaults to `1`).
        markdown : bool
            Whether to use Markdown to parse the text string (defaults to `True`).
        keep_linebreaks : bool
            Whether to replace newline characters (`\\n`) with HTML linebreaks (`<br>`). Defaults to `True`, but is only
            relevant when `markdown = False`.
        """

        # TODO: decide what to do with css_class
        css_class = ""

        textbox = TextBox(content, row, column, row_span, col_span, markdown, keep_linebreaks)
        self._check_grid_pos(row, column)
        self._elements.append(textbox)

    def add_plotly_figure(self, fig: Figure, row: int, column: int, row_span: int = 1, col_span: int = 1):
        """Add a Plotly_ figure to this slide, in the specified row and column.

        .. _Plotly: https://www.plotly.com

        Parameters
        ----------
        fig: plotly.graph_objects.Figure
            A Plotly Figure object.
        row: int
            The grid row in which to place this plot.
        column: int
            The grid column in which to place this plot.
        row_span: optional, int
            The number of rows for this plot to span (defaults to `1`).
        col_span: optional, int
            The number of columns for this plot to span (defaults to `1`).

        """

        plotly_figure = PlotlyFigure(fig, row, column, row_span, col_span)
        self._check_grid_pos(row, column)
        self._elements.append(plotly_figure)

    def add_image(self, image_path: Union[str, Path], row: int, column: int, row_span: int = 1, col_span: int = 1,
                  width_pct: int = 100):
        """Add an image to this slide, in the specified row and column.

        Parameters
        ----------
        image_path: str or pathlib.Path
            A string or pathlib.Path object representing the path to the image.
        row: int
            The grid row in which to place this image.
        column: int
            The grid column in which to place this image.
        row_span: optional, int
            The number of rows for this image to span (defaults to `1`).
        col_span: optional, int
            The number of columns for this image to span (defaults to `1`).
        width_pct: optional, int
            The percentage of the original image width to scale by. Defaults to 100 (no resizing).
        """

        image = Image(image_path, row, column, row_span, col_span, width_pct)
        self._check_grid_pos(row, column)
        self._elements.append(image)

    # TODO: preview() function