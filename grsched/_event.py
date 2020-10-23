from typing import List

from datetimerange import DateTimeRange
from tcolorpy import tcolor


class Object:
    def __init__(self, id: int, name: str, code: str) -> None:
        self.id = id
        self.name = name
        self.code = code


class User(Object):
    pass


class Facility(Object):
    pass


class Event:
    def __init__(self, **kwargs) -> None:
        self.id = int(kwargs["id"])
        self.creator = User(**kwargs["creator"])
        self.created_at = kwargs["createdAt"]
        self.updater = User(**kwargs["updater"])
        self.updated_at = kwargs["updatedAt"]
        self.event_menu = kwargs["eventMenu"]
        self.subject = kwargs["subject"]
        self.notes = kwargs["notes"].replace("\r\n", "\n")
        self.is_all_day = kwargs["isAllDay"]
        self.attendees = []
        self.facilities = []

        if "facilities" in kwargs:
            for data in kwargs["facilities"]:
                self.facilities.append(Facility(**data))

        for data in kwargs["attendees"]:
            if data["type"] not in ["USER", "ORGANIZATION"]:
                continue

            self.attendees.append(User(data["id"], data["name"], data["code"]))

        self.timezone = kwargs["start"]["timeZone"]
        self.dtr = DateTimeRange(
            start_datetime=kwargs["start"]["dateTime"],
            end_datetime=kwargs["end"]["dateTime"],
        )
        self.dtr.start_time_format = "%Y/%m/%d %H:%M"
        self.dtr.end_time_format = "%H:%M"

    def as_row(self, is_all_day: bool) -> List:
        if is_all_day:
            self.dtr.start_time_format = "%Y/%m/%d"
            self.dtr.end_time_format = "all day"

        return [self.id, self.dtr, self.__make_subject()]

    def as_markdown(self) -> str:
        h1_color = "cyan"
        h2_color = "light cyan"

        lines = [
            tcolor("# {}".format(self.__make_subject()), color=h1_color),
            tcolor("## Date and time", color=h2_color),
            str(self.dtr),
            "",
        ]

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
                    tcolor("## Attendees ({} users)".format(len(self.attendees)), color=h2_color),
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
                "- Registrant: {}  {}".format(self.creator.name, self.created_at),
                "- Updater: {}  {}".format(self.updater.name, self.updated_at),
            ]
        )

        return "\n".join(lines)

    def __make_subject(self) -> str:
        if self.event_menu:
            return "{}: {}".format(self.event_menu, self.subject)

        return "{}".format(self.subject)

    def __make_attendees_block(self) -> str:
        threshold = 10
        block = ", ".join([user.name for user in self.attendees[:threshold]])

        if len(self.attendees) < threshold:
            return block

        return block + " ..."
