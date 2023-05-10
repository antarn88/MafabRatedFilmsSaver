from json import dumps
from bs4 import BeautifulSoup
from requests import Response, get
from urllib3 import disable_warnings, exceptions

from film_downloader import FilmDownloader
from my_types import FilmsDict

print("Mafab Rated Films Saver 1.23\n")
mafab_user_id = input("Kérem a Mafab user ID-t: ")
print()
current_page = 1
last_page = 1
films_counter = 0
downloaded_films = 0
filmsDict: FilmsDict = {"films": []}
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    " AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
}

disable_warnings(exceptions.InsecureRequestWarning)

while True:
    mafab_current_url = f"https://www.mafab.hu/user/{mafab_user_id}/ertekelesek/&page={current_page}"
    response: Response

    try:
        response = get(mafab_current_url, headers=headers, verify=False)
    except Exception as ex:
        print(f"Meghiúsúlt az oldalletöltés! Az utolsó sikeres oldal: {current_page}")
        print(f"Részletek: {ex}")
        break

    if response:
        soup = BeautifulSoup(response.text, "lxml")
        if current_page == 1:
            h_counter = soup.select_one(".heading-box .h-counter")
            if h_counter is not None:
                films_counter = int(h_counter.text.replace("(", "").replace(")", ""))
                if soup.select(".pagination li.hidden-xs a"):
                    last_page = int(soup.select(".pagination li.hidden-xs a")[-1].text)
                else:
                    last_page = 1
        film_rows = soup.select(".profile-content-item")
        for film_row in film_rows:
            movie_title = film_row.select_one(".movie_title")
            if movie_title is not None:
                film_name = str(movie_title.text).strip()
                movie_title_link = film_row.select_one(".movie_title_link")
                if movie_title_link is not None:
                    film_link = f"https://www.mafab.hu{str(movie_title_link.get('href')).strip()}"
                    stars = film_row.select_one(".pci-movie-row-stars span")
                    if stars is not None:
                        film_rating = str(stars.get("title")).strip()
                        film_downloader = FilmDownloader(film_link, film_rating)
                        filmsDict.get("films").append(film_downloader.get_film_data())
                        downloaded_films += 1
                        print(f"\rLetöltött filmadatok a memóriába: {downloaded_films}/{films_counter}", end="")
        if current_page == last_page:
            break
        else:
            current_page += 1
    else:
        print(f"Meghiúsúlt az oldalletöltés! Az utolsó sikeres oldal: {current_page}")
        break

try:
    json: str = dumps(filmsDict, ensure_ascii=False)
    json_file = open("films.json", "w", encoding="utf-8")
    json_file.write(json)
    json_file.close()
    input("\nA JSON fájl sikeresen elkészült.")
except:
    input("\nHiba történt a JSON fájl elkészítésekor!")
