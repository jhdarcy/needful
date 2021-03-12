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
    row_span: optional, int
        The number of rows for this plot to span (defaults to `1`).
    col_span: optional, int
        The number of columns for this plot to span (defaults to `1`).
    markdown: optional, bool
        Whether to use Markdown to parse the text string (defaults to `True`).
    keep_linebreaks: optional, bool
        Whether to replace newline characters (`\\n`) with HTML linebreaks (`<br>`). Defaults to `True`, but is only
        relevant when `markdown = False`.
    """

    def __init__(self,
                 content: str,
                 row: int,
                 column: int,
                 row_span: int = 1,
                 col_span: int = 1,
                 markdown: bool = True,
                 keep_linebreaks: bool = True
                 ):
        check_type("content", content, str)
        self.content = content

        self._check_and_set(row, column, row_span, col_span)

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

        # TODO: do I want to have the an additional css class option here?

        if self.keep_linebreaks and not self.markdown:
            text = self.content.replace("\n", "<br>")
        else:
            text = self.content

        # TODO: decide best markup syntax for hidden asterisk footnotes.
        # hovernotes = re.findall("<hovernote>(.*)</hovernote>", self.text)
        # for i, hovernote in enumerate(hovernotes):
        #     astericks = r"\*" * (i + 1)
        #     replacement_text = f"<span class='hover-note'>{astericks}</span><span class='hover-box note'>{hovernote}</span>"
        #     find_text = f"<hovernote>{hovernote}</hovernote>"
        #     text = text.replace(find_text, replacement_text, 1)

        if self.markdown:
            md = Markdown()
            text = md.convert(text)

        return f"<div {self._style_str} class=\"textbox\">{text}</div>"
