from bs4 import BeautifulSoup, ResultSet, Tag
from requests import RequestException, Response, get

from my_types import Film

headers: dict[str, str] = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    " AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
}


class FilmDownloader:
    def __init__(self, film_link: str, film_rating: str):
        self.__film_link: str = film_link
        self.__film_rating: str = film_rating

    def __get_film_genres(self) -> list[str]:
        genres: list[str] = []
        film_page: BeautifulSoup | None = self.__get_film_page()
        if film_page is not None:
            genres_a_tags: ResultSet[Tag] = film_page.select(".mp-genres a")
            if genres_a_tags:
                for genre_a_tag in genres_a_tags:
                    genres.append(str(genre_a_tag.text).strip())
        return genres

    def get_film_id(self) -> int:
        film_page: BeautifulSoup | None = self.__get_film_page()
        if film_page is not None:
            if film_page.select("#star_rating_modal"):
                star_rating_modal: Tag | None = film_page.select_one("#star_rating_modal")
                if star_rating_modal is not None:
                    return int(str(star_rating_modal.get("data-movie-id")).strip())
        return 0

    def __get_film_stars(self) -> int | None:
        return {"None": 0, "Rossz": 1, "Gyenge": 2, "Átlagos": 3, "Jó": 4, "Zseniális": 5}.get(self.__film_rating)

    def __get_film_page(self) -> BeautifulSoup | None:
        try:
            response: Response = get(self.__film_link, headers=headers, verify=False, timeout=None)
            if response:
                return BeautifulSoup(response.text, "lxml")
            print(f"Meghiúsult filmletöltés! A film linkje: {self.__film_link}")
            return None
        except RequestException as ex:
            print(f"Meghiúsult filmletöltés! A film linkje: {self.__film_link}")
            print(f"A hiba részletei: {ex}")
            return None

    def __get_film_name(self) -> str:
        film_page: BeautifulSoup | None = self.__get_film_page()
        if film_page is not None:
            h1_title: Tag | None = film_page.select_one(".mp-title-right h1")
            if h1_title is not None:
                return str(h1_title.contents[0]).strip()
        return ""

    def __get_film_year(self) -> int:
        film_page: BeautifulSoup | None = self.__get_film_page()
        if film_page is not None:
            h1_span: Tag | None = film_page.select_one(".mp-title-right h1 span")
            if h1_span is not None:
                try:
                    return int(str(h1_span.text).strip().replace("(", "").replace(")", ""))
                except ValueError:
                    return int(str(h1_span.text).strip().replace("(", "").replace(")", "").split("-", maxsplit=1)[0])
                except AttributeError:
                    return 0
        return 0

    def __get_film_poster(self) -> str:
        film_page: BeautifulSoup | None = self.__get_film_page()
        if film_page is not None:
            poster_img: Tag | None = film_page.select_one("#poster_img")
            if poster_img is not None:
                return str(poster_img.get("src")).strip().replace("thumb/w150/", "")
        return ""

    def __get_film_keywords(self) -> list[str]:
        keywords: list[str] = []
        film_page: BeautifulSoup | None = self.__get_film_page()
        if film_page is not None:
            if film_page.select(".tagsContainer"):
                tags_container: Tag | None = film_page.select_one(".tagsContainer")
                if tags_container is not None:
                    a_tags: ResultSet[Tag] = tags_container.select("a")
                    for a_tag in a_tags:
                        keywords.append(str(a_tag.text).strip())
        return keywords

    def get_film_data(self) -> Film:
        return {
            "id": self.get_film_id(),
            "name": self.__get_film_name(),
            "year": self.__get_film_year(),
            "stars": self.__get_film_stars(),
            "url": self.__film_link,
            "poster": self.__get_film_poster(),
            "keywords": self.__get_film_keywords(),
            "genres": self.__get_film_genres(),
        }
