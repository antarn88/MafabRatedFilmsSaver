from bs4 import BeautifulSoup
from requests import get

from my_types import Film

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    " AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
}


class FilmDownloader:
    def __init__(self, film_link: str, film_rating: str):
        self.film_link = film_link
        self.film_rating = film_rating

    def get_film_genres(self) -> list[str]:
        genres: list[str] = []
        film_page = self.get_film_page()
        if film_page is not None:
            genres_a_tags = film_page.select(".mp-genres a")
            if genres_a_tags:
                for genre_a_tag in genres_a_tags:
                    genres.append(str(genre_a_tag.text).strip())
        return genres

    def get_film_id(self) -> int:
        film_page = self.get_film_page()
        if film_page is not None:
            if film_page.select("#star_rating_modal"):
                star_rating_modal = film_page.select_one("#star_rating_modal")
                if star_rating_modal is not None:
                    return int(str(star_rating_modal.get("data-movie-id")).strip())
        return 0

    def get_film_stars(self) -> int | None:
        return {"None": 0, "Rossz": 1, "Gyenge": 2, "Átlagos": 3, "Jó": 4, "Zseniális": 5}.get(self.film_rating)

    def get_film_page(self) -> BeautifulSoup | None:
        try:
            response = get(self.film_link, headers=headers, verify=False)
            if response:
                return BeautifulSoup(response.text, "lxml")
            else:
                print(f"Meghiúsult filmletöltés! A film linkje: {self.film_link}")
                return None
        except Exception as ex:
            print(f"Meghiúsult filmletöltés! A film linkje: {self.film_link}")
            print(f"A hiba részletei: {ex}")
            return None

    def get_film_name(self) -> str:
        film_page = self.get_film_page()
        if film_page is not None:
            h1_title = film_page.select_one(".mp-title-right h1")
            if h1_title is not None:
                return str(h1_title.contents[0]).strip()
        return ""

    def get_film_year(self) -> int:
        film_page = self.get_film_page()
        if film_page is not None:
            h1_span = film_page.select_one(".mp-title-right h1 span")
            if h1_span is not None:
                try:
                    return int(str(h1_span.text).strip().replace("(", "").replace(")", ""))
                except ValueError:
                    return int(str(h1_span.text).strip().replace("(", "").replace(")", "").split("-")[0])
                except AttributeError:
                    return 0
        return 0

    def get_film_poster(self) -> str:
        film_page = self.get_film_page()
        if film_page is not None:
            poster_img = film_page.select_one("#poster_img")
            if poster_img is not None:
                return str(poster_img.get("src")).strip().replace("thumb/w150/", "")
        return ""

    def get_film_keywords(self) -> list[str]:
        keywords: list[str] = []
        film_page = self.get_film_page()
        if film_page is not None:
            if film_page.select(".tagsContainer"):
                tags_container = film_page.select_one(".tagsContainer")
                if tags_container is not None:
                    a_tags = tags_container.select("a")
                    for a_tag in a_tags:
                        keywords.append(str(a_tag.text).strip())
        return keywords

    def get_film_data(self) -> Film:
        return {
            "id": self.get_film_id(),
            "name": self.get_film_name(),
            "year": self.get_film_year(),
            "stars": self.get_film_stars(),
            "url": self.film_link,
            "poster": self.get_film_poster(),
            "keywords": self.get_film_keywords(),
            "genres": self.get_film_genres(),
        }
