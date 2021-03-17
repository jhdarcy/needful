from base64 import b64encode
from io import BytesIO, StringIO
from typing import Optional

from matplotlib.figure import Figure as _Figure

from .grid_object import GridObject
from .._utils import check_type


class MPLFigure(GridObject):
    """Represents a Matplotlib figure.

    Parameters
    ----------
    fig: matplotlib.figure.Figure
        A string or pathlib.Path object representing the path to the image, OR a BinaryIO object representing the
        contents of the image (for internal use only).
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
    def __init__(self,
                 fig: _Figure,
                 row: int,
                 column: int,
                 row_span: int = 1,
                 col_span: int = 1,
                 config: Optional[dict] = None
                 ):

        # Check provided image_path is either string or Path object, then check that it exists.
        check_type("fig", fig, _Figure)
        self.fig = fig
        self.config = config if config is not None else {}

        # Check if user has set format - if so, we'll need to distinguish between SVG and pixel images.
        if "format" in self.config:
            if self.config["format"].lower() == "svg":
                self.fmt = "svg"
                self.fig_out = StringIO()
            elif self.config["format"].lower() == "pdf":
                raise ValueError("PDF format not supported for Matplotlib figures. Try format='svg' or format='png'.")
            else:
                # Assume everything else will work...
                self.fmt = "png"
                self.fig_out = BytesIO()
        else:
            self.fmt = "png"
            self.fig_out = BytesIO()

        self.fig.savefig(self.fig_out, **self.config)
        self._check_and_set(row, column, row_span, col_span)

    def get_div(self) -> str:
        """Get the required <div></div> HTML tags to display this plot.

        Returns
        -------
        str
        """
        # Write this figure to BytesIO.

        self.fig_out.seek(0)

        if self.fmt == "png":
            img = b64encode(self.fig_out.read()).decode()
            img_style_str = f'style="justify-self:center"'
            html_str = f'<div {self._style_str}><center><img src="data:image;base64, {img}" {img_style_str}></center></div>'
        elif self.fmt == "svg":
            svg = self.fig_out.read()
            html_str = f'<div {self._style_str}><center>{svg}</center></div>'
        else:
            raise RuntimeError("We should not be here.")

        return html_str




