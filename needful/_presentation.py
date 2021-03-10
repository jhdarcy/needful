from pathlib import Path
from typing import Optional, Union

from jinja2 import Environment, FileSystemLoader
import webbrowser

from ._utils import check_exists, check_type
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
    mathjax : bool, default=False
        Whether to load MathJax to display equations. Defaults to `False`.
    """
    def __init__(self,
                 title: str,
                 css_file: Optional[Union[str, Path]] = None,
                 page_numbers: bool = True,
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
            Self explanatory.
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
        open_file: optional, bool
            Whether to open the resulting file (defaults to `True`).
        """
        check_type("filename", filename, Union[str, Path])
        check_type("open_file", open_file, bool)

        if len(self.slides) == 0:
            print("No slides to render! Abort.")
            return

        env = Environment(loader=FileSystemLoader(str(self._static_dir)), trim_blocks=True, lstrip_blocks=True)
        template = env.get_template(self._html_template.name)

        # Total number of Plotly plots in this presentation, use this to determine whether
        # the presentation should load Plotly.
        n_plots = sum([slide.n_plots for slide in self.slides])
        plotly = n_plots > 0

        # Read in the CSS stylesheet to insert into the HTML document.
        with open(self._css_file, 'r') as f:
            css = "".join(f.readlines())

        # Extract the :root CSS variables, if present.
        # css_root_str = re.search(r":root\s*{.*?}", css, flags=re.MULTILINE | re.DOTALL)
        #
        # if css_root_str:
        #     # :root { ... } match found
        #     css_root_str = css_root_str[0]

        # TODO: some trickery to warn if a CSS variable is defined in a theme, but not the main CSS stylesheet.

        # Render the HTML!
        template_vars = {
            "css_style": css,
            "mathjax": self.mathjax,
            "plotly": plotly,
            "slides": self.slides,
            "title": self.title,
            "css_themes": self._css_themes,
            "page_numbers": self.page_numbers,
            "config_var": "needfulConfig"
        }
        self.html_out = template.render(template_vars)

        file_path = Path(filename).absolute()
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(self.html_out)

        if open_file:
            url = "file:///" + str(file_path).replace("\\", "/").replace(" ", "%20")
            webbrowser.open(url)
