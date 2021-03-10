from typing import Union
from pathlib import Path


def check_type(var_name: str, var: object, expected_type: Union[type, object]) -> None:
    """
    A handy little typechecker - use to strictly enforce types.
    """

    # Do some junk to check expected_type - is it a normal base type, or some abomination from the typing module?
    # https://stackoverflow.com/a/49471187
    if hasattr(expected_type, "__origin__"):
        # Assume of type Union for the moment, update this if I ever get errors from here.
        # Here, expected_type.__args__ contains the base types (string, int, etc.) we need, and can be passed into
        # isinstance below.
        type_expected = expected_type.__args__
        if len(type_expected) == 1:
            type_name = type_expected[0].__name__
        else:
            type_name = ", ".join([t.__name__ for t in type_expected[:-1]]) + f" or {type_expected[-1].__name__}"
    else:
        type_expected = expected_type
        type_name = type_expected.__name__

    if not isinstance(var, type_expected):
        raise TypeError(f"Variable {var_name} is of type {type(var).__name__}; expected {type_name}.")


def check_exists(path: Union[str, Path], name: str, file: bool = True):
    """Check whether the given path exists. This is a noisy utility function, and will raise an Exception if the file
    or directory does not exist."""
    ExceptionType = FileNotFoundError if file else NotADirectoryError
    p = Path(path)
    is_not_file = file and not p.is_file()
    if not p.exists() or is_not_file:
        raise ExceptionType(f"{name} not found at {str(p.absolute())}.")


def check_sanity_int(var_name: str, var: int):
    """A simple sanity checker for row/column/layout integer variables. Must be integer and > 0."""
    check_type(var_name, var, int)
    if var < 1:
        raise ValueError(f"{var_name} must be greater than 0. Received {var_name} = {var}.")

