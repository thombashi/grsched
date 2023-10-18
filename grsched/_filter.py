from datetime import datetime
from typing import Any, Final, List, Optional, Union

from datetimerange import DateTimeRange
from pytablewriter.style import Cell, Style
from tcolorpy import Color


GRAY: Final[Color] = Color("8f8f8f")
DARK_GRAY: Final[Color] = Color("#0f0f0f")
DARK_RED: Final[Color] = Color("#8B0000")
DARK_YELLOW: Final[Color] = Color("#554913")


def _calc_other_ground_color(color: Color) -> Color:
    invert_threshold = 385

    if (color.red + color.green + color.blue) > invert_threshold:
        return Color("black")

    return color


def col_separator_style_filter(
    lcell: Optional[Cell], rcell: Optional[Cell], **kwargs: Any
) -> Optional[Style]:
    cell = lcell if lcell else rcell
    if cell is None:
        return None

    if cell.is_header_row():
        return None

    dtrs: Final[List[DateTimeRange]] = kwargs["dtrs"]
    dtr: Final[DateTimeRange] = dtrs[cell.row]
    now: Final[datetime] = kwargs["now"]

    fg_color: Union[Color, str, None] = None
    bg_color: Union[Color, str, None] = None

    if now in dtr:
        bg_color = DARK_RED
    elif dtr.end_datetime and dtr.end_datetime.date() == now.date():
        bg_color = DARK_YELLOW

    if fg_color or bg_color:
        return Style(color=fg_color, bg_color=bg_color)

    return None


def style_filter(cell: Cell, **kwargs: Any) -> Optional[Style]:
    if cell.is_header_row():
        return None

    dtrs: Final[List[DateTimeRange]] = kwargs["dtrs"]
    dtr: Final[DateTimeRange] = dtrs[cell.row]
    now: Final[datetime] = kwargs["now"]
    ended_event: Final[bool] = True if dtr.end_datetime and dtr.end_datetime < now else False

    fg_color: Union[Color, str, None] = None
    bg_color: Union[Color, str, None] = None

    if ended_event:
        fg_color = GRAY

    if now in dtr:
        bg_color = DARK_RED
    elif dtr.end_datetime and dtr.end_datetime.date() == now.date():
        bg_color = DARK_YELLOW

    if fg_color or bg_color:
        return Style(color=fg_color, bg_color=bg_color)

    return None
