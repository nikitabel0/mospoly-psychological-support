from dataclasses import dataclass

from psychohelp.models.users import User


@dataclass(frozen=True, slots=True)
class UserWithToken:
    user: User
    token: str