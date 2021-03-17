from re import compile as compile_regex
from re import DOTALL
from secrets import token_hex
from typing import Optional

from plotly.graph_objects import Figure as _Figure

from .grid_object import GridObject
from .._utils import check_type


class PlotlyFigure(GridObject):
    """Represents a Plotly figure, with an additional function to return the Plotly.newPlot(...) JS code.

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
    config: optional, dict
        A dictionary containing plot configuration options to be passed to Plotly.js.
    """

    def __init__(self,
                 fig: _Figure,
                 row: int,
                 column: int,
                 row_span: int = 1,
                 col_span: int = 1,
                 config: Optional[dict] = None
                 ):
        check_type("fig", fig, _Figure)
        self.fig = fig
        self.config = config

        self._check_and_set(row, column, row_span, col_span)

        # Generate a better ID for this figure - we'll use this later.
        self.fig_id = token_hex(5)

    def get_js(self) -> str:
        """Get the Javascript Plotly.newPlot(...) function for this plot. The Figure object is converted to its full
        HTML presentation via the fig.to_html(...) function, from which the relevant Javascript is extracted.

        Note: the required <div> tags for the plot are generated by the `get_div()` function.

        Returns
        -------
        str
            The Plotly.newPlot(...) function for this plot.
        """
        plotly_html = self.fig.to_html(include_plotlyjs=False, full_html=False, auto_play=False)
                                       #default_width='100%', default_height='100%')

        # Only keep the Plotly.newPlot(...) part of the HTML string above - it contains everything we need.
        # Use a quick hit of RegEx.
        regex = compile_regex("Plotly.newPlot\(.*\)", flags=DOTALL)
        plotly_str = regex.findall(plotly_html)[0]

        # Extract the div id - we'll replace it with something more sensible.
        regex = compile_regex('div id=\".*?\"')
        div_id = regex.findall(plotly_html)[0]
        orig_id = compile_regex('\".*"').findall(div_id)[0].replace('"', '')

        # Replace the generated div id with the shorter figure ID.
        plotly_js_str = plotly_str.replace(orig_id, self.fig_id)
        return plotly_js_str

    def get_div(self) -> str:
        """Get the required <div></div> HTML tags to display this plot.

        Returns
        -------
        str
        """
        div_str = f'<div {self._style_str} id="{self.fig_id}" class="plotdiv"></div>'
        return div_str

    def __str__(self):
        return self.get_div()
