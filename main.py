from json import dumps
from bs4 import BeautifulSoup, ResultSet, Tag
from requests import RequestException, Response, get
from urllib3 import disable_warnings, exceptions

from film_downloader import FilmDownloader
from my_types import FilmsDict

print("Mafab Rated Films Saver 1.24\n")
mafab_user_id: str = input("Kérem a Mafab user ID-t: ")
print()
current_page: int = 1
last_page: int = 1
films_counter: int = 0
downloaded_films: int = 0
filmsDict: FilmsDict = {"films": []}
headers: dict[str, str] = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    " AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
}

disable_warnings(exceptions.InsecureRequestWarning)

while True:
    mafab_current_url: str = f"https://www.mafab.hu/user/{mafab_user_id}/ertekelesek/&page={current_page}"
    response: Response

    try:
        response = get(mafab_current_url, headers=headers, verify=False, timeout=None)
    except RequestException as ex:
        print(f"Meghiúsúlt az oldalletöltés! Az utolsó sikeres oldal: {current_page}")
        print(f"Részletek: {ex}")
        break

    if response:
        soup: BeautifulSoup = BeautifulSoup(response.text, "lxml")
        if current_page == 1:
            h_counter: Tag | None = soup.select_one(".heading-box .h-counter")
            if h_counter is not None:
                films_counter = int(h_counter.text.replace("(", "").replace(")", ""))
                if soup.select(".pagination li.hidden-xs a"):
                    last_page = int(soup.select(".pagination li.hidden-xs a")[-1].text)
                else:
                    last_page = 1  # pylint: disable=invalid-name
        film_rows: ResultSet[Tag] = soup.select(".profile-content-item")
        for film_row in film_rows:
            movie_title: Tag | None = film_row.select_one(".movie_title")
            if movie_title is not None:
                movie_title_link: Tag | None = film_row.select_one(".movie_title_link")
                if movie_title_link is not None:
                    film_link: str = f"https://www.mafab.hu{str(movie_title_link.get('href')).strip()}"
                    stars: Tag | None = film_row.select_one(".pci-movie-row-stars span")
                    if stars is not None:
                        FILM_RATING: str = str(stars.get("title")).strip()
                        film_downloader: FilmDownloader = FilmDownloader(film_link, FILM_RATING)
                        filmsDict.get("films").append(film_downloader.get_film_data())
                        downloaded_films += 1
                        print(f"\rLetöltött filmadatok a memóriába: {downloaded_films}/{films_counter}", end="")
        if current_page == last_page:
            break
        current_page += 1
    else:
        print(f"Meghiúsúlt az oldalletöltés! Az utolsó sikeres oldal: {current_page}")
        break

try:
    json_str = dumps(filmsDict, ensure_ascii=False)
    with open("films.json", "w", encoding="utf-8") as json_file:
        json_file.write(json_str)
    input("\nA JSON fájl sikeresen elkészült.")
except (FileNotFoundError, PermissionError, IOError, TypeError) as e:
    input("\nHiba történt a JSON fájl elkészítésekor: " + str(e))
