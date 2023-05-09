from typing import TypedDict


class Film(TypedDict):
    id: int
    name: str
    year: int
    stars: int | None
    url: str
    poster: str
    keywords: list[str]
    genres: list[str]


class FilmsDict(TypedDict):
    films: list[Film]


__all__ = ["Film", "FilmsDict"]
