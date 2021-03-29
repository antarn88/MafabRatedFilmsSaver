from json import dumps

from bs4 import BeautifulSoup
from requests import get

from FilmDownloader import FilmDownloader

print("Mafab Rated Films Saver 1.1\n")
mafab_user_id = input("Kérem a Mafab user ID-t: ")
print()
current_page = 1
last_page = 1
films_counter = 0
download_films = 0
films = {"films": []}
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                         " AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36"}

while True:
    mafab_current_url = f"https://www.mafab.hu/user/{mafab_user_id}/ertekelesek/&page={current_page}"
    soup = BeautifulSoup(get(mafab_current_url, headers=headers).text, "lxml")
    if current_page == 1:
        films_counter = int(soup.select_one(".heading-box .h-counter").text.replace("(", "").replace(")", ""))
        if soup.select(".pagination li.hidden-xs a"):
            last_page = int(soup.select(".pagination li.hidden-xs a")[-1].text)
        else:
            last_page = 1
    film_rows = soup.select(".profile-content-item")
    for film_row in film_rows:
        film_name = str(film_row.select_one(".movie_title").text).strip()
        film_link = f"https://www.mafab.hu{str(film_row.select_one('.movie_title_link').get('href')).strip()}"
        film_rating = str(film_row.select_one(".pci-movie-row-stars span").get("title")).strip()
        film_downloader = FilmDownloader(film_link, film_rating)
        films.get("films").append(film_downloader.get_film_data())
        download_films += 1
        print(f"\rLetöltött filmadatok a memóriába: {download_films}/{films_counter}", end="")
    if current_page == last_page:
        break
    else:
        current_page += 1

try:
    json = dumps(films, ensure_ascii=False)
    json_file = open("films.json", "w", encoding="utf-8")
    json_file.write(json)
    json_file.close()
    input("\nA JSON fájl sikeresen elkészült.")
except:
    input("\nHiba történt a JSON fájl elkészítésekor!")
