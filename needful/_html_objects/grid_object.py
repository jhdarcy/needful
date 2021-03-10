from abc import ABC, abstractmethod

from .._utils import check_sanity_int


class GridObject(ABC):
    """A base class defining an object - text box, image, plot, etc. - that will be placed on the CSS grid."""
    @abstractmethod
    def __init__(self):
        pass

    def _check_and_set(self, row: int, column: int, row_span: int, col_span: int) -> None:
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

    @abstractmethod
    def get_div(self) -> str:
        pass

    @property
    def _style_str(self):
        css_str = f"grid-column : {self.column} / {self.column + self.col_span}; grid-row : {self.row} / {self.row + self.row_span};"
        style_str = f'style="{css_str}"'
        return style_str

    def __str__(self):
        return self.get_div()
