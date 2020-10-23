from typing import Union  # noqa
from typing import Optional

from pytablewriter.style import Cell, Style
from tcolorpy import Color


DEFAULT_COLOR = Color("white")


def _calc_other_ground_color(color: Color) -> Color:
    invert_threshold = 385

    if (color.red + color.green + color.blue) > invert_threshold:
        return Color("black")

    return color


def col_separator_style_filter(lcell: Cell, rcell: Cell, **kwargs) -> Optional[Style]:
    fg_color = None  # type: Union[Color, str, None]
    bg_color = None  # type: Union[Color, str, None]
    row = lcell.row if lcell else rcell.row
    col = lcell.col if lcell else rcell.col
    dtrs = kwargs["dtrs"]
    now = kwargs["now"]
    color = DEFAULT_COLOR
    is_end = dtrs[row].end_datetime <= now

    if row < 0:
        return None

    if row % 2 == 0:
        fg_color = _calc_other_ground_color(color)
        if is_end:
            bg_color = "#afafaf"
        else:
            bg_color = "light white"
    else:
        fg_color = color

    if is_end:
        fg_color = "light black"

    if fg_color or bg_color:
        return Style(color=fg_color, bg_color=bg_color)

    return None


def style_filter(cell: Cell, **kwargs) -> Optional[Style]:
    fg_color = None  # type: Union[Color, str, None]
    bg_color = None  # type: Union[Color, str, None]
    dtrs = kwargs["dtrs"]
    now = kwargs["now"]
    color = DEFAULT_COLOR
    is_end = dtrs[cell.row].end_datetime <= now

    if cell.row < 0:
        return None

    elif cell.row % 2 == 0:
        fg_color = _calc_other_ground_color(color)
        if is_end:
            bg_color = "#afafaf"
        else:
            bg_color = "light white"
    else:
        fg_color = color

    if is_end:
        fg_color = "light black"

    if fg_color or bg_color:
        return Style(color=fg_color, bg_color=bg_color)

    return None
