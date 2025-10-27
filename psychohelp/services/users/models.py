from dataclasses import dataclass

from psychohelp import models


@dataclass(frozen=True, slots=True)
class UserWithToken:
    user: models.User
    token: str