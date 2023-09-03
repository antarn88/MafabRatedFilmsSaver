from bs4 import BeautifulSoup, Tag
from requests import RequestException, Response, get

from custom_types import Film

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
        film_page = self.__get_film_page()
        if film_page is not None:
            selector = ".movie_quick_info .film-info-span a"
            genre_links = film_page.select(selector, href=lambda x: x and "genre=" in x)  # type: ignore
            if genre_links:
                genres = [link.text.strip() for link in genre_links]  # type: ignore
                genres = list(set(genres))
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
            movie_quick_info_tag = None

            if (film_page_tag := film_page.select_one(".movie_quick_info")) is not None:
                movie_quick_info_tag = film_page_tag.find("div", {"class": "film-info-span"})

            if movie_quick_info_tag:
                try:
                    year_tag = movie_quick_info_tag.contents[0]  # type: ignore
                    return int(year_tag.strip())  # type: ignore
                except (TypeError, AttributeError):
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
            keyword_tags = film_page.select(".kulcszo")
            keywords = [tag.text.strip() for tag in keyword_tags]
            keywords = list(set(keywords))
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
