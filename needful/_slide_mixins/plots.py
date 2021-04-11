from typing import Optional

from .mixin import SlideMixin
from .._utils import check_type


class PlotMixin(SlideMixin):
    """Adds plot functionality to the Slide class."""
    @property
    def _plotly_figs(self):
        return [e for e in self._elements if e.__class__.__name__ == "PlotlyFigure"]

    @property
    def _bokeh_figs(self):
        return [e for e in self._elements if e.__class__.__name__ == "BokehFigure"]

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

            from ._bokeh_figure import BokehFigure
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
            from ._mpl_figure import MPLFigure

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
            from ._plotly_figure import PlotlyFigure

            # Only need to check type of plotly_config here, as row/column/etc are checked below.
            check_type("plotly_config", plotly_config, Optional[dict])

            fig = PlotlyFigure(figure_object, row, column, row_span, col_span, css_class, plotly_config)

        else:
            raise RuntimeError("We should not be here!")

        self._check_grid_pos(row, column)
        self._elements.append(fig)
