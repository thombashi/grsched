from dataclasses import dataclass
from typing import Any, Dict, Final, List, Optional

import pytz
from datetimerange import DateTimeRange
from tcolorpy import tcolor


@dataclass(frozen=True)
class Object:
    id: int
    name: str
    code: str


class User(Object):
    pass


@dataclass(frozen=True)
class Organization(Object):
    childOrganizations: List[Dict[str, str]]
    parentOrganization: str


class Facility(Object):
    pass


class Event:
    def __init__(self, **kwargs: Any) -> None:
        self.id = int(kwargs["id"])
        self.creator = User(**kwargs["creator"])
        self.created_at: str = kwargs["createdAt"]
        self.updater = User(**kwargs["updater"])
        self.updated_at: str = kwargs["updatedAt"]
        self.event_type: str = kwargs["eventType"]
        self.event_menu: str = kwargs["eventMenu"]
        self.subject: str = kwargs["subject"]
        self.notes: str = kwargs["notes"].replace("\r\n", "\n")
        self.attendees: List[User] = []
        self.facilities: List[Facility] = []

        if "facilities" in kwargs:
            for data in kwargs["facilities"]:
                self.facilities.append(Facility(**data))

        for data in kwargs["attendees"]:
            if data["type"] not in ["USER", "ORGANIZATION"]:
                continue

            self.attendees.append(User(data["id"], data["name"], data["code"]))

        self.dtr: Optional[DateTimeRange] = None

        if "start" not in kwargs and self.event_type == "REPEATING":
            print()
            print(kwargs["repeatInfo"])
            repeat_info = kwargs["repeatInfo"]
            self.is_all_day: bool = repeat_info["isAllDay"]
            self.timezone = pytz.timezone(repeat_info["timeZone"])
        else:
            self.is_all_day = kwargs["isAllDay"]
            self.timezone = pytz.timezone(kwargs["start"]["timeZone"])
            self.dtr = DateTimeRange(
                start_datetime=kwargs["start"]["dateTime"],
                end_datetime=kwargs["end"]["dateTime"],
                timezone=self.timezone,
            )
            self.dtr.start_time_format = "%Y/%m/%d %H:%M"
            self.dtr.end_time_format = "%H:%M"

    def as_row(self, is_all_day: bool) -> List:
        if is_all_day and self.dtr:
            self.dtr.start_time_format = "%Y/%m/%d"
            self.dtr.end_time_format = "all day"

        return [self.id, self.dtr, self.__make_subject()]

    def as_markdown(self) -> str:
        h1_color: Final[str] = "cyan"
        h2_color: Final[str] = "light cyan"

        lines = [
            tcolor(f"# {self.__make_subject()}", color=h1_color),
            "",
        ]

        if self.dtr:
            lines.extend(
                [
                    tcolor("## Date and time", color=h2_color),
                    str(self.dtr),
                    "",
                ]
            )

        if self.facilities:
            lines.extend(
                [
                    tcolor("## Facilities", color=h2_color),
                    ", ".join([facility.name for facility in self.facilities]),
                    "",
                ]
            )

        if self.attendees:
            lines.extend(
                [
                    tcolor(f"## Attendees ({len(self.attendees)} users)", color=h2_color),
                    self.__make_attendees_block(),
                    "",
                ]
            )

        if self.notes:
            lines.extend([tcolor("## Notes", color=h2_color), self.notes])

        lines.extend(
            [
                "",
                "---",
                f"- Registrant: {self.creator.name}  {self.created_at}",
                f"- Updater: {self.updater.name}  {self.updated_at}",
            ]
        )

        return "\n".join(lines)

    def __make_subject(self) -> str:
        if self.event_menu:
            return f"{self.event_menu}: {self.subject}"

        return f"{self.subject}"

    def __make_attendees_block(self) -> str:
        threshold = 10
        block = ", ".join([user.name for user in self.attendees[:threshold]])

        if len(self.attendees) < threshold:
            return block

        return block + " ..."
