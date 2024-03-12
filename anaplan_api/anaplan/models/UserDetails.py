from dataclasses import dataclass
from datetime import datetime

from anaplan_api.anaplan.util.strtobool import strtobool


@dataclass
class UserDetails(object):
    _user_details: dict
    _email: str
    _id: str
    _active: bool
    _email_opt_in: bool
    _last_login: datetime

    def __init__(self, details: dict):
        """
        :param details: JSON details for specified user
        :type details: dict
        """
        self._user_details = details
        self._id = details["id"]
        self._email = details["email"]
        self._active = strtobool(str(details["active"]))
        self._email_opt_in = strtobool(str(details["emailOptIn"]))
        self._last_login = datetime.strptime(
            str(details["lastLoginDate"]), "%Y-%m-%dT%H:%M:%S.%f%z"
        )

    def __str__(self) -> str:
        """Return details for specified user

        :return: User details
        :rtype: str
        """
        return f"Email: {self._email}, ID: {self._id}, Active: {self._active}, Last login: {self._last_login}"
