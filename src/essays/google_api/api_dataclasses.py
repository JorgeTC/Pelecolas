from dataclasses import dataclass


class ApiDataclass:

    def __init__(self, **args) -> None:
        for param in self.__slots__:
            setattr(self, param, args.get(param))


@dataclass(slots=True, init=False)
class Post(ApiDataclass):
    title: str
    url: str
    content: str
    published: str
    updated: str
    id: str
    labels: list[str]
    kind: str = "blogger#post"


@dataclass(slots=True, init=False)
class DriveFile(ApiDataclass):
    name: str
    id: str
    trashed: bool


@dataclass(slots=True, init=False)
class Blog(ApiDataclass):
    id: str
    name: str
    url: str
    kind: str = "blogger#blog"
