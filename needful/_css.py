from secrets import token_hex


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