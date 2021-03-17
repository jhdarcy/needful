# Standard module imports
from io import BytesIO
from pathlib import Path
from secrets import token_hex
from typing import Optional, Union

# Third-party module imports
from plotly.graph_objects import Figure

# From this module
from ._css import CSSTheme
from ._html_objects import TextBox, Image, PlotlyFigure
from ._preview import preview_slide
from ._utils import check_type


class Slide:
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
            raise ValueError(
"Slide title and menu title are blank. If the title is to be left blank, then menu_title needs to be set."
            )
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

    def add_plot(self,
                 figure_object,
                 row: int,
                 column: int,
                 row_span: int = 1,
                 col_span: int = 1,
                 matplotlib_params: Optional[dict] = None,
                 plotly_config: Optional[dict] = None
                 ):
        """Add a plot to this slide, in the specified row and column. The plot may be a Plotly or Matplotlib figure.

        Parameters
        ----------
        figure_object : matplotlib.figure.Figure or plotly.graph_objs.Figure
            A Matplotlib or Plotly Figure object. The figure must implement the `.savefig(...)` function if generated by
            Matplotlib, or `.to_html(...)` if it is generated by Plotly.
        row: int
            The grid row in which to place this plot.
        column: int
            The grid column in which to place this plot.
        row_span: int, default=1
            The number of rows for this plot to span (defaults to `1`).
        col_span: int, default=1
            The number of columns for this plot to span (defaults to `1`).
        matplotlib_params: dict, optional
            An optional dictionary containing arguments to pass to the Matplotlib `savefig` function. See:
            https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.savefig.html
        plotly_config: dict, optional
            An optional dictionay containing configuration options to pass to Plotly.js. See:
            https://plotly.com/python/configuration-options/
        """

        # Don't want to import classes unless the figure actually belongs to them, so we'll quickly check the
        # type of figure_object by name only. Something about this rubs me the wrong way, but it'll do for the moment.
        # (Ultimately, I'm doing this so all the supported plotting libraries *don't* become automatic dependencies of
        # the needful module.)
        supported_libs = ["matplotlib", "plotly"]

        fig_module = figure_object.__class__.__module__.lower()

        if not any([lib in fig_module for lib in supported_libs]):
            raise TypeError(
                f"Unknown figure_object passed to add_plot. Received figure of type {figure_object.__class__.__name__}."
            )

        if "plotly" in fig_module:
            # Double check we have a Plotly figure, not some other Plotly paraphernalia.
            if type(figure_object).__name__.lower() != 'figure':
                raise TypeError(
f"Unknown Plotly object passed to add_plot. Please provide a valid plotly.graph_objs.Figure object. Received figure of type {figure_object.__class__.__name__}."
                )

            # Finally, we may proceed.
            from ._html_objects import PlotlyFigure

            # Only need to check type of plotly_config here, as row/column/etc are checked below.
            check_type("plotly_config", plotly_config, Optional[dict])

            fig = PlotlyFigure(figure_object, row, column, row_span, col_span, plotly_config)

        elif "matplotlib" in fig_module:
            # Double check we have a Matplotlib figure, not some other MPL paraphernalia.
            if type(figure_object).__name__.lower() != 'figure':
                raise TypeError(
f"Unknown Matplotlib object passed to add_plot. Please provide a valid matplotlib.figure.Figure object. Received figure of type {figure_object.__class__.__name__}."
                )

            # Finally, we may proceed.
            from ._html_objects import MPLFigure

            # Only need to check type of matplotlib_params here, as row/column/etc are checked below.
            check_type("matplotlib_params", matplotlib_params, Optional[dict])

            fig = MPLFigure(figure_object, row, column, row_span, col_span, matplotlib_params)
        else:
            raise RuntimeError("We should not be here!")

        self._check_grid_pos(row, column)
        self._elements.append(fig)

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
        row_span: int, default=1
            The number of rows for this image to span (defaults to `1`).
        col_span: int, default=1
            The number of columns for this image to span (defaults to `1`).
        width_pct: int, default=100
            The percentage of the original image width to scale by. Defaults to 100 (no resizing).
        """

        image = Image(image_path, row, column, row_span, col_span, width_pct)
        self._check_grid_pos(row, column)
        self._elements.append(image)

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



