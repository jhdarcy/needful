from abc import ABC, abstractmethod
from typing import Optional

from .._utils import check_sanity_int, check_type


class GridObject(ABC):
    """A base class defining an object - text box, image, plot, etc. - that will be placed on the CSS grid."""
    @abstractmethod
    def __init__(self):
        pass

    def _check_and_set(self, row: int, column: int, row_span: int, col_span: int, css_class: Optional[str]) -> None:
        """A quick checker and setter for the row and column attributes of this CSS grid object."""
        check_sanity_int("row", row)
        check_sanity_int("column", column)
        check_sanity_int("row_span", row_span)
        check_sanity_int("col_span", col_span)

        # If any of the above failed, an exception would have been thrown. Proceed to set these variables.
        self.row = row
        self.column = column
        self.row_span = row_span
        self.col_span = col_span

        check_type("css_class", css_class, Optional[str])

        if css_class:
            if css_class.strip() == "":
                css_class = None

        self.css_class = css_class

    @abstractmethod
    def get_div(self) -> str:
        pass

    @property
    def _style_str(self):
        css_str = f"grid-column : {self.column} / {self.column + self.col_span}; grid-row : {self.row} / {self.row + self.row_span};"

        if self.css_class:
            class_str = f' class="{self.css_class}"'
        else:
            class_str = ""

        style_str = f'style="{css_str}"{class_str}'
        return style_str

    def __str__(self):
        return self.get_div()
