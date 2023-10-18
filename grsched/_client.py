import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import retryrequests

from ._const import LIMIT, MODULE_NAME
from ._event import Event, Organization, User
from ._logger import logger  # type: ignore


class GaroonClient:
    def __init__(self, subdomain: str, basic_auth: str) -> None:
        if not subdomain:
            logger.error(f"require a valid subdomain. try '{MODULE_NAME} configure' first.")
            sys.exit(1)

        self.__subdomain = "{}.cybozu.com".format(subdomain.strip().rstrip(".cybozu.com"))
        self.__basic_auth = basic_auth

        logger.debug(f"subdomain: {self.__subdomain}")

    def fetch_event(self, id: int) -> Event:
        response = retryrequests.get(
            url=self.__make_url(endpoint="schedule/events", id=id),
            headers=self.__make_headers(),
        )
        response.raise_for_status()

        return Event(**response.json())

    def fetch_events(
        self,
        start: Optional[datetime],
        days: int,
        target: Optional[str] = None,
        target_type: Optional[str] = None,
    ) -> Tuple[List[Event], bool]:
        params = self.__make_params(start=start, days=days)
        if target:
            params["target"] = target
        if target_type:
            params["targetType"] = target_type

        response = retryrequests.get(
            url=self.__make_url(endpoint="schedule/events"),
            headers=self.__make_headers(),
            params=params,
        )
        response.raise_for_status()
        data = response.json()

        return ([Event(**event) for event in data["events"]], data["hasNext"])

    def fetch_users(
        self,
        offset: int,
    ) -> Tuple[List[User], bool]:
        response = retryrequests.get(
            url=self.__make_url(endpoint="base/users"),
            headers=self.__make_headers(),
            params={"limit": LIMIT, "offset": offset},
        )
        response.raise_for_status()
        data = response.json()

        return ([User(**user) for user in data["users"]], data["hasNext"])

    def fetch_organizations(
        self,
        offset: int,
    ) -> Tuple[List[Organization], bool]:
        response = retryrequests.get(
            url=self.__make_url(endpoint="base/organizations"),
            headers=self.__make_headers(),
            params={"limit": LIMIT, "offset": offset},
        )
        response.raise_for_status()
        data = response.json()

        return ([Organization(**org) for org in data["organizations"]], data["hasNext"])

    def __make_headers(self) -> Dict[str, str]:
        return {
            "Host": f"{self.__subdomain}:443",
            "X-Cybozu-Authorization": self.__basic_auth,
        }

    def __make_params(self, start: Optional[datetime] = None, days: int = 7) -> Dict:
        params = {
            "limit": LIMIT,
            "fields": ",".join(
                [
                    "id",
                    "creator",
                    "createdAt",
                    "updater",
                    "updatedAt",
                    "eventType",
                    "eventMenu",
                    "subject",
                    "notes",
                    "visibilityType",
                    "isAllDay",
                    "isStartOnly",
                    "attendees",
                    "facilities",
                    "start",
                    "end",
                    "additionalItems",
                ]
            ),
            "orderBy": "start asc",
        }

        if start is not None:
            params["rangeStart"] = start.isoformat("T")
            params["rangeEnd"] = (start + timedelta(days=days)).isoformat("T")

        return params

    def __make_url(self, endpoint: str, id: Optional[int] = None) -> str:
        url = f"https://{self.__subdomain}/g/api/v1/{endpoint}"
        if id is not None:
            url = f"{url}/{id}"

        return url
