

class SlideMixin:

    _elements = []

    def _check_grid_pos(self, row: int, column: int) -> None:
        raise RuntimeError("This is implemented by the Slide class. We should not be here.")

    def __init__(self):
        raise RuntimeError("Attempt to directly initialise SlideMixin. We should not be here.")
