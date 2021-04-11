from typing import Optional

from markdown import Markdown

from .grid_object import GridObject
from .._utils import check_type


class TextBox(GridObject):
    """Represents a textbox on the slide.

    Parameters
    ----------
    content: str
        A string containing the content of this textbox. May contain HTML and/or Markdown formatting.
    row: int
        The grid row in which to place this plot.
    column: int
        The grid column in which to place this plot.
    row_span: int, default=1
        The number of rows for this plot to span (defaults to `1`).
    col_span: int, default=1
        The number of columns for this plot to span (defaults to `1`).
    markdown: bool, default=True
        Whether to use Markdown to parse the text string (defaults to `True`).
    keep_linebreaks: bool, default=True
        Whether to replace newline characters (`\\n`) with HTML linebreaks (`<br>`). Defaults to `True`, but is only
        relevant when `markdown = False`.
    css_class: str, optional
        The name of the CSS class (or classes) to apply to this object.
    """

    def __init__(self,
                 content: str,
                 row: int,
                 column: int,
                 row_span: int = 1,
                 col_span: int = 1,
                 markdown: bool = True,
                 keep_linebreaks: bool = True,
                 css_class: Optional[str] = None,
                 ):
        check_type("content", content, str)
        self.content = content

        self._check_and_set(row, column, row_span, col_span, css_class)

        if self.css_class:
            if "textbox" not in self.css_class:
                self.css_class += " textbox"
        else:
            self.css_class = "textbox"

        check_type("markdown", markdown, bool)
        self.markdown = markdown
        check_type("keep_linebreaks", keep_linebreaks, bool)
        self.keep_linebreaks = keep_linebreaks

    def get_div(self):
        """Get the required <div></div> HTML tags to display this textbox.

        Returns
        -------
        str
        """

        if self.keep_linebreaks and not self.markdown:
            text = self.content.replace("\n", "<br>")
        else:
            text = self.content

        if self.markdown:
            extensions = ["tables", "fenced_code"]
            md = Markdown(extensions=extensions)
            text = md.convert(text)

        # If there are any backticks (`) present in the text, convert it to its HTML entity (&#96;).
        text = text.replace("`", "&#96;")

        return f"<div {self._style_str}>{text}</div>"
