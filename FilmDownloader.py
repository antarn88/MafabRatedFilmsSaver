from bs4 import BeautifulSoup
from requests import get
from random import randint

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                         " AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36"}


class FilmDownloader:
    def __init__(self, film_link, film_rating):
        self.film_link = film_link
        self.film_rating = film_rating

    def get_film_genres(self):
        genres = []
        genres_a_tags = self.get_film_page().select(".mp-genres a")
        if genres_a_tags:
            for genre_a_tag in genres_a_tags:
                genres.append(str(genre_a_tag.text).strip())
        return genres

    def get_film_id(self):
        return int(str(self.get_film_page().select_one("#star_rating_modal").get("data-movie-id")).strip())

    def get_film_stars(self):
        return {"None": 0, "Rossz": 1, "Gyenge": 2, "Átlagos": 3, "Jó": 4, "Zseniális": 5}.get(self.film_rating)

    def get_film_page(self):
        return BeautifulSoup(get(self.film_link, headers=headers).text, "lxml")

    def get_film_name(self):
        return str(self.get_film_page().select_one(".mp-title-right h1").contents[0]).strip()

    def get_film_year(self):
        try:
            return int(str(self.get_film_page().select_one(".mp-title-right h1 span").text)
                       .strip().replace("(", "").replace(")", ""))
        except ValueError:
            return int(str(self.get_film_page().select_one(".mp-title-right h1 span").text)
                       .strip().replace("(", "").replace(")", "").split("-")[0])
        except AttributeError:
            return 0

    def get_film_poster(self):
        return str(self.get_film_page().select_one("#poster_img").get("src")).strip().replace("thumb/w150/", "")

    def get_film_keywords(self):
        keywords = []
        if self.get_film_page().select(".tagsContainer"):
            a_tags = self.get_film_page().select_one(".tagsContainer").select("a")
            for a_tag in a_tags:
                keywords.append(str(a_tag.text).strip())
        return keywords

    def get_description(self):
        return "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt."

    def get_price(self):
        return randint(999, 4999)

    # Original version
    def get_film_data(self):
        return {
            "id": self.get_film_id(),
            "name": self.get_film_name(),
            "year": self.get_film_year(),
            "stars": self.get_film_stars(),
            "url": self.film_link,
            "poster": self.get_film_poster(),
            "keywords": self.get_film_keywords(),
            "genres": self.get_film_genres()
        }

    

    # Modified version
    # def get_film_data(self):
    #    return {
    #       "name": self.get_film_name(),
    #       "description": self.get_description(),
    #       "price": self.get_price(),
    #       "photo": self.get_film_poster(),
    #      "active": True
    #    }
