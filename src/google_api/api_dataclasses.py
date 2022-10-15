from dataclasses import dataclass
from typing import Any


class ApiDataclass:

    def __init__(self, **dict: dict[str, Any]) -> None:
        for param in self.__slots__:
            setattr(self, param, dict.get(param))


@dataclass(slots=True, init=False)
class Post(ApiDataclass):
    title: str
    url: str
    content: str
    published: str
    updated: str
    kind: str = "blogger#post"
    id: str
    labels: str


@dataclass(slots=True, init=False)
class DriveFile(ApiDataclass):
    name: str
    id: str
    trashed: bool


@dataclass(slots=True, init=False)
class Blog(ApiDataclass):
    id: str
    kind: str = "blogger#blog"
    name: str
    url: str
