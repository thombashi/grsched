import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import retryrequests

from ._const import LIMIT, MODULE_NAME, RFC3339
from ._event import Event, User
from ._logger import logger


class GaroonClient:
    def __init__(self, subdomain: str, basic_auth: str) -> None:
        if not subdomain:
            logger.error("require a valid subdomain. try '{} configure' first.".format(MODULE_NAME))
            sys.exit(1)

        self.__subdomain = "{}.cybozu.com".format(subdomain.strip().rstrip(".cybozu.com"))
        self.__basic_auth = basic_auth

        logger.debug("subdomain: {}".format(self.__subdomain))

    def fetch_event(self, id: int) -> Event:
        response = retryrequests.get(
            url=self.__make_url(endpoint="schedule/events", id=id),
            headers=self.__make_headers(),
            params=self.__make_params(),
        )
        response.raise_for_status()

        return Event(**response.json())

    def fetch_events(
        self,
        start: Optional[datetime],
        target: Optional[str] = None,
        target_type: Optional[str] = None,
    ) -> Tuple[List[Event], bool]:
        params = self.__make_params(start=start)
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

    def __make_headers(self) -> Dict[str, str]:
        return {
            "Host": "{}:443".format(self.__subdomain),
            "X-Cybozu-Authorization": self.__basic_auth,
        }

    def __make_params(self, start: Optional[datetime] = None) -> Dict:
        params = {
            "limit": LIMIT,
            "fields": ",".join(
                [
                    "id",
                    "creator",
                    "createdAt",
                    "updater",
                    "updatedAt",
                    "eventMenu",
                    "subject",
                    "notes",
                    "isAllDay",
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
            params["rangeStart"] = start.strftime(RFC3339)
            params["rangeEnd"] = (start + timedelta(days=3)).strftime(RFC3339)

        return params

    def __make_url(self, endpoint: str, id: Optional[int] = None) -> str:
        url = "https://{}/g/api/v1/{}".format(self.__subdomain, endpoint)
        if id is not None:
            url = "{}/{}".format(url, id)

        return url
