from pathlib import Path
from typing import Optional, Union

from jinja2 import Environment, FileSystemLoader
import webbrowser

from ._utils import check_exists, check_type, check_sanity_int
from ._slide import Slide


class Presentation:
    """Represents a needful HTML presentation.

    Parameters
    ----------
    title : str
        The title of this presentation. This will be displayed in the browser's title/tab bar.
    css_file : str, Path, optional
        The .css file controlling the overall styling of this presentation. If left blank, the presentation will use the
        default needful style.
    page_numbers : bool, default=True
        Whether to display page numbers on each slide. Defaults to `True`, and can be overridden at an individual slide
        level if needed.
    navigation_menu : bool, default=True
        Whether to display the hidden navigation menu when the mouse hovers over the page number. Defaults to `True`,
        and can be overridden at an individual slide level if needed.
    autoscale : bool, default=True
        Whether to automatically scale the presentation up/down to best fit the window. Defaults to `True`, and can be
        overridden at an individual slide level if required.
    width : int, default=1280
        The base width of this presentation, in pixels. The presentation will be scaled up or down relative to this
        width. Defaults to 1280px, and only takes effect when `autoscale = True`.
    height : int, default=720
        The base height of this presentation, in pixels. The presentation will be scaled up or down relative to this
        height. Defaults to 720px, and only takes effect when `autoscale = True`.
    allow_overflow : bool, default=False
        Whether slide contents are allowed to overflow beyond the presentation window. If set to `True`, slide contents
        can extend beyond the bounds of the window, and normal browser scrolling is permitted. If `False`, content
        extending beyond the presentation window will be cut off. Defaults to `False`, and only applies when `autoscale
        = True`. Can be overridden at an individual slide level if required.
    mathjax : bool, default=False
        Whether to load MathJax to display equations. Defaults to `False`.
    """
    def __init__(self,
                 title: str,
                 css_file: Optional[Union[str, Path]] = None,
                 page_numbers: bool = True,
                 navigation_menu: bool = True,
                 autoscale: bool = True,
                 width: int = 1280,
                 height: int = 720,
                 allow_overflow: bool = False,
                 mathjax: bool = False
                 ):

        self.slides = []

        check_type("title", title, str)
        self.title = title

        # Check if static directory exists, along with HTML template and CSS file.

        self._static_dir = Path(__file__).parent.joinpath("static")
        check_exists(self._static_dir, "'static' folder", file=False)

        self._html_template = self._static_dir.joinpath("template.html")
        check_exists(self._html_template, "HTML template")

        check_type("css_file", css_file, Optional[Union[str, Path]])
        if not css_file:
            # No CSS file provided - use default.css
            self._css_file = self._static_dir.joinpath("default.css")
            check_exists(self._css_file, "default.css")
        else:
            self._css_file = Path(css_file)
            check_exists(self._css_file, css_file)

        check_type("page_numbers", page_numbers, bool)
        self.page_numbers = page_numbers

        check_type("navigation_menu", navigation_menu, bool)
        self.nav_menu = navigation_menu

        check_type("width", width, int)
        check_sanity_int("width", width)
        self.width = width

        check_type("height", height, int)
        check_sanity_int("height", height)
        self.height = height

        check_type("autoscale", autoscale, bool)
        self.autoscale = autoscale

        check_type("allow_overflow", allow_overflow, bool)
        self.overflow = allow_overflow

        check_type("mathjax", mathjax, bool)
        self.mathjax = mathjax

        self.html_out = ""
        self._css_themes = []

    def add_slide(self, slide: Slide):
        """Add a new slide to this presentation.

        Parameters
        ----------
        slide : needful.Slide
        """
        check_type("slide", slide, Slide)
        self.slides.append(slide)

        if slide.theme is not None:
            css_theme_ids = [theme.id for theme in self._css_themes]
            if slide.theme.id not in css_theme_ids:
                self._css_themes.append(slide.theme)

    def add_slides(self, slide_list: list):
        """Add a list of Slides to this presentation.

        Parameters
        ----------
        slide_list : list
            Self-explanatory.
        """
        check_type("slide_list", slide_list, list)
        for slide in slide_list:
            self.add_slide(slide)

    def generate_html(self, filename: Union[str, Path], open_file: bool = True):
        """Save the HTML presentation to the given file and open in the default browser.

        Parameters
        ----------
        filename: str or pathlib.Path
            A string or pathlib.Path object representing the HTML file.
        open_file: bool, default=True
            Whether to open the resulting file (defaults to `True`).
        """
        check_type("filename", filename, Union[str, Path])
        check_type("open_file", open_file, bool)

        if len(self.slides) == 0:
            print("No slides to render! Abort.")
            return

        env = Environment(loader=FileSystemLoader(str(self._static_dir)), trim_blocks=True, lstrip_blocks=True)
        template = env.get_template(self._html_template.name)

        needs_bokeh = any([slide.needs_bokeh for slide in self.slides])
        if needs_bokeh:
            # Get the Bokeh.js CDN details.
            from bokeh.resources import CDN
            bokeh_cdn = CDN.render()
        else:
            bokeh_cdn = ""

        needs_plotly = any([slide.needs_plotly for slide in self.slides])

        # Read in the CSS stylesheet to insert into the HTML document.
        with open(self._css_file, 'r') as f:
            css = "".join(f.readlines())

        # Render the HTML!
        template_vars = dict(
            css_style=css,
            slides=self.slides,
            title=self.title,
            size=(self.width, self.height),
            autoscale=self.autoscale,
            overflow=self.overflow,
            mathjax=self.mathjax,
            plotly=needs_plotly,
            bokeh=bokeh_cdn,
            css_themes=self._css_themes,
            page_numbers=self.page_numbers,
            nav_menu=self.nav_menu,
            config_var="needfulConfig"
        )
        self.html_out = template.render(template_vars)

        file_path = Path(filename).absolute()
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(self.html_out)

        if open_file:
            url = "file:///" + str(file_path).replace("\\", "/").replace(" ", "%20")
            webbrowser.open(url)
