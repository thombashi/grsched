from typing import Any, Final, Optional, Union

from pytablewriter.style import Cell, Style
from tcolorpy import Color


GRAY: Final[Color] = Color("#bfbfbf")


def _calc_other_ground_color(color: Color) -> Color:
    invert_threshold = 385

    if (color.red + color.green + color.blue) > invert_threshold:
        return Color("black")

    return color


def col_separator_style_filter(
    lcell: Optional[Cell], rcell: Optional[Cell], **kwargs: Any
) -> Optional[Style]:
    fg_color: Union[Color, str, None] = None
    bg_color: Union[Color, str, None] = None

    cell = lcell if lcell else rcell
    if cell is None:
        return None

    if cell.is_header_row():
        return None

    row = cell.row
    dtrs = kwargs["dtrs"]
    now = kwargs["now"]

    if row < 0:
        return None

    is_end = dtrs[row].end_datetime <= now
    ddays = max(0, dtrs[row].end_datetime.day - now.day)
    n = max(0, 255 - ddays * 32)
    bg_color = Color((n, n, n))
    fg_color = "black"

    if is_end:
        fg_color = GRAY

    if fg_color or bg_color:
        return Style(color=fg_color, bg_color=bg_color)

    return None


def style_filter(cell: Cell, **kwargs: Any) -> Optional[Style]:
    fg_color: Union[Color, str, None] = None
    bg_color: Union[Color, str, None] = None
    dtrs = kwargs["dtrs"]
    now = kwargs["now"]

    if cell.row < 0:
        return None

    is_end = dtrs[cell.row].end_datetime <= now
    ddays = max(0, dtrs[cell.row].end_datetime.day - now.day)
    n = max(0, 255 - ddays * 32)
    bg_color = Color((n, n, n))
    fg_color = "black"

    if is_end:
        fg_color = GRAY

    if fg_color or bg_color:
        return Style(color=fg_color, bg_color=bg_color)

    return None
