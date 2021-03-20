# Standard module imports
from pathlib import Path
from secrets import token_hex
from typing import Optional, Union

# From this module
from ._css import CSSTheme
from ._html_objects import TextBox, Image
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
    def _plotly_figs(self):
        return [e for e in self._elements if e.__class__.__name__ == "PlotlyFigure"]

    @property
    def _bokeh_figs(self):
        return [e for e in self._elements if e.__class__.__name__ == "BokehFigure"]

    @property
    def html(self):
        # Stitch together HTML string.
        return "\n".join([str(element) for element in self._elements])

    @property
    def js_plot_func(self):
        plots = self._bokeh_figs + self._plotly_figs
        if len(plots) > 0:
            plot_funcs = [f"{plot.get_plot_js()};" for plot in plots]
            return "\n".join(plot_funcs)
        else:
            return "return"

    @property
    def js_purge_func(self):
        if self.needs_bokeh or self.needs_plotly:
            purge_funcs = ""
            if self.needs_bokeh:
                purge_funcs += "\nBokeh.documents.forEach((doc) => doc.clear());\nBokeh.documents.length = 0;"
            if self.needs_plotly:
                plotly_purge_funcs = [f"Plotly.purge('{plot.fig_id}');" for plot in self._plotly_figs]
                purge_funcs += "\n".join(plotly_purge_funcs)
        else:
            purge_funcs = "return"

        return purge_funcs

    @property
    def needs_plotly(self):
        return len(self._plotly_figs) > 0

    @property
    def needs_bokeh(self):
        return len(self._bokeh_figs) > 0

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

    def add_textbox(self,
                    content: str,
                    row: int,
                    column: int,
                    row_span: int = 1,
                    col_span: int = 1,
                    css_class: Optional[str] = None,
                    markdown: bool = True,
                    keep_linebreaks: bool = True) -> None:
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
        row_span : int, default=1
            The number of rows for this textbox to span (defaults to `1`).
        col_span : int, default=1
            The number of columns for this textbox to span (defaults to `1`).
        css_class : str, optional
            The CSS class (or classes) to apply to this textbox. Multiple CSS classes are applied in a single string,
            separated by a space. I.e. `css_class = "class1 class2"`.
        markdown : bool, default=True
            Whether to use Markdown to parse the text string (defaults to `True`).
        keep_linebreaks : bool, default=True
            Whether to replace newline characters (`\\n`) with HTML linebreaks (`<br>`). Defaults to `True`, but is only
            relevant when `markdown = False`.
        """

        textbox = TextBox(content, row, column, row_span, col_span, markdown, keep_linebreaks, css_class)
        self._check_grid_pos(row, column)
        self._elements.append(textbox)

    def add_plot(self,
                 figure_object,
                 row: int,
                 column: int,
                 row_span: int = 1,
                 col_span: int = 1,
                 css_class: Optional[str] = None,
                 bokeh_theme: Optional = None,
                 matplotlib_params: Optional[dict] = None,
                 plotly_config: Optional[dict] = None
                 ):
        """Add a plot to this slide, in the specified row and column. The plot may be a Bokeh, Plotly or Matplotlib
        figure.

        Parameters
        ----------
        figure_object : bokeh.plotting.figure.Figure, matplotlib.figure.Figure, matplotlib.axes.Axes or plotly.graph_objs.Figure
            A Bokeh `Figure`, Matplotlib `Axes`/`Figure`, or Plotly `Figure` object. If a Matplotlib object, the object
            must implement the `get_figure()` or `savefig(...)` function. If a Plotly object, then the `.to_html(...)`
            function must be present.
        row: int
            The grid row in which to place this plot.
        column: int
            The grid column in which to place this plot.
        row_span: int, default=1
            The number of rows for this plot to span (defaults to `1`).
        col_span: int, default=1
            The number of columns for this plot to span (defaults to `1`).
        css_class : str, optional
            The CSS class (or classes) to apply to this plot. Multiple CSS classes are applied in a single string,
            separated by a space. I.e. `css_class = "class1 class2"`.
        bokeh_theme: bokeh.themes.theme.Theme, optional
            A Bokeh Theme object representing the theme to apply to the plot. If left as None, then the default Bokeh
            theme will be used. See:
            https://docs.bokeh.org/en/latest/docs/reference/themes.html#bokeh-themes
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
        supported_libs = ["bokeh", "matplotlib", "plotly"]

        fig_module = figure_object.__class__.__module__.lower()

        if not any([lib in fig_module for lib in supported_libs]):
            raise TypeError(
                f"Unknown figure_object passed to add_plot. Received figure of type {figure_object.__class__.__name__}."
            )

        if "bokeh" in fig_module:
            # I'm not that familiar with Bokeh yet, so for a faux type-check I think I'll just attempt to call Bokeh's
            # json_item function and re-raise any exceptions as a TypeError.
            from bokeh.embed import json_item

            try:
                _ = json_item(figure_object, bokeh_theme)
            except Exception as e:
                raise TypeError(f"Unknown Bokeh object passed to add_plot. Bokeh raised the following Exception:\n\t{e.__class__.__name__}: {e.args[0]}")

            # If we're here, I think we're good... maybe?
            # TODO: more certainty/confidence with Bokeh

            from ._html_objects import BokehFigure
            fig = BokehFigure(figure_object, row, column, row_span, col_span, css_class, bokeh_theme)

        elif "matplotlib" in fig_module:
            # Double check we have a Matplotlib Figure or Axes object, not some other MPL paraphernalia.
            if not hasattr(figure_object, "get_figure") and not hasattr(figure_object, "savefig"):
                raise TypeError(
                    f"Unknown Matplotlib object passed to add_plot. Please provide a valid matplotlib Figure or Axes object. Received object of type {figure_object.__class__.__name__}."
                )

            # If an MPL axis-type object has been provided, call the get_figure() function.
            if not hasattr(figure_object, "savefig"):
                mpl_fig = figure_object.get_figure()
            else:
                mpl_fig = figure_object

            # Finally, we may proceed.
            from ._html_objects import MPLFigure

            # Only need to check type of matplotlib_params here, as row/column/etc are checked below.
            check_type("matplotlib_params", matplotlib_params, Optional[dict])

            fig = MPLFigure(mpl_fig, row, column, row_span, col_span, css_class, matplotlib_params)

        elif "plotly" in fig_module:
            # Double check we have a Plotly figure, not some other Plotly paraphernalia.
            if not hasattr(figure_object, "to_html"):
                raise TypeError(
                    f"Unknown Plotly object passed to add_plot. Please provide a valid plotly.graph_objs.Figure object. Received object of type {figure_object.__class__.__name__}."
                )

            # Finally, we may proceed.
            from ._html_objects import PlotlyFigure

            # Only need to check type of plotly_config here, as row/column/etc are checked below.
            check_type("plotly_config", plotly_config, Optional[dict])

            fig = PlotlyFigure(figure_object, row, column, row_span, col_span, css_class, plotly_config)

        else:
            raise RuntimeError("We should not be here!")

        self._check_grid_pos(row, column)
        self._elements.append(fig)

    def add_image(self,
                  image_path: Union[str, Path],
                  row: int,
                  column: int,
                  row_span: int = 1,
                  col_span: int = 1,
                  width_pct: int = 100,
                  css_class: Optional[str] = None,
                  ):
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
        css_class : str, optional
            The CSS class (or classes) to apply to this image. Multiple CSS classes are applied in a single string,
            separated by a space. I.e. `css_class = "class1 class2"`.
        """

        image = Image(image_path, row, column, row_span, col_span, width_pct, css_class)
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



