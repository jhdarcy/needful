from base64 import b64encode

from pathlib import Path
from typing import Optional, Union

from PIL import Image as PILImage

from .grid_object import GridObject
from .._utils import check_exists, check_type, check_sanity_int


class Image(GridObject):
    """Represents an image on the slide.

    Parameters
    ----------
    image_file: str, pathlib.Path or
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
    css_class: str, optional
        The name of the CSS class (or classes) to apply to this object.
    """

    def __init__(self,
                 image_path: Union[str, Path],
                 row: int,
                 column: int,
                 row_span: int = 1,
                 col_span: int = 1,
                 width_pct: int = 100,
                 css_class: Optional[str] = None
                 ):

        # Check provided image_path is either string or Path object, then check that it exists.
        check_type("image_path", image_path, Union[str, Path])
        check_exists(image_path, "Image")
        self.image_file = image_path

        self._check_and_set(row, column, row_span, col_span, css_class)

        check_sanity_int("width_pct", width_pct)
        self.width_pct = width_pct

    def get_div(self) -> str:
        """Get the required <div></div> HTML tags to display this image.

        Returns
        -------
        str
        """
        # Read in the image, convert to string with Base64.
        with open(self.image_file, 'rb') as f:
            img = b64encode(f.read()).decode()
            # Use Pillow to also open the image and get its size - we'll use this to scale the image if we need to.
            img_size = PILImage.open(f).size

        img_width = int(self.width_pct / 100 * img_size[0])

        img_style_str = f'style="justify-self:center"'
        html_str = f'<div {self._style_str}><center><img src="data:image;base64, {img}" {img_style_str} width={img_width}px></center></div>'
        return html_str




