from datetime import datetime
from pathlib import Path
from secrets import token_hex
import shutil
from typing import Union

from ._utils import check_exists, check_type


def get_default_css(destination_file: Union[str, Path]):
    """Copies the needful `default.css` file to the specified file/path. The destination file will be backed up if it
     already exists so you don't irreversibly clobber an existing .css file.

     Parameters
     ----------
     destination_file: str, pathlib.Path
        The name or path to the destination file.
     """
    check_type("destination_file", destination_file, Union[str, Path])
    dest_path = Path(destination_file)

    # Sanity check - has user accidentally provided a directory instead of a file name?
    if dest_path.is_dir():
        raise IsADirectoryError(f"destination_file: {dest_path} is a directory, not a file. Please provide a file name.")

    # Back up file if it exists.
    if dest_path.exists():
        backup_name = dest_path.name + f".bak_{datetime.today():%Y_%m_%d_%H.%M.%S}"
        print(f"{dest_path.name} already exists. Backing up to {backup_name}.")
        dest_path.rename(backup_name)

    static_dir = Path(__file__).parent.joinpath("static")
    check_exists(static_dir, "'static' folder", file=False)

    default_css = static_dir.joinpath("default.css")
    check_exists(default_css, "default.css")

    shutil.copy(default_css, dest_path)


class CSSTheme:
    """Represents a CSS theme that can be applied to one or more slides."""
    def __init__(self):
        self.id = token_hex(5)
        self._css_dict = {}

    def __getitem__(self, key: str):
        # Strip the -- from the start of the string, in case they've been included.
        return self._css_dict[key.lstrip('-')]

    def __setitem__(self, key: str, value: str):
        if not isinstance(key, str):
            raise TypeError("Non-string type provided as name of CSS variable.")

        if not isinstance(value, str):
            raise TypeError("Non-string type provided as value of CSS variable.")

        # Strip the -- from the start of the string, in case they've been included.
        self._css_dict[key.lstrip('-')] = value

        # space reserved for any further checks

    def __repr__(self):
        str_list = [f"--{key}: {val};" for key, val in self._css_dict.items()]
        return "\n".join(str_list)

    def get_js(self) -> str:
        """Returns the JavaScript representation of this CSS theme. Here, the JavaScript representation is
        a list of tuples, with the CSS variable name in the first entry, followed by the value of that
        variable. E.g. [['--main-background-color', 'black'], ['--main-font-color', 'white']]
        """
        key_val_list = [f"[\"--{key}\", \"{val}\"]" for key, val in self._css_dict.items()]
        return f"[{', '.join(key_val_list)}]"