from json import dumps

from bs4 import BeautifulSoup
from requests import get
from urllib3 import disable_warnings, exceptions

from FilmDownloader import FilmDownloader

print("Mafab Rated Films Saver 1.22\n")
mafab_user_id = input("Kérem a Mafab user ID-t: ")
print()
current_page = 1
last_page = 1
films_counter = 0
download_films = 0
films = {"films": []}
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

                         " AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36"}

disable_warnings(exceptions.InsecureRequestWarning)

while True:
    mafab_current_url = f"https://www.mafab.hu/user/{mafab_user_id}/ertekelesek/&page={current_page}"
    response = None

    try:
        response = get(mafab_current_url, headers=headers, verify=False)
    except Exception as ex:
        print(
            f"Meghiúsúlt az oldalletöltés! Az utolsó sikeres oldal: {current_page}")
        print(f"Részletek: {ex}")
        break

    if response:
        soup = BeautifulSoup(response.text, "lxml")
        if current_page == 1:
            films_counter = int(soup.select_one(
                ".heading-box .h-counter").text.replace("(", "").replace(")", ""))
            if soup.select(".pagination li.hidden-xs a"):
                last_page = int(soup.select(
                    ".pagination li.hidden-xs a")[-1].text)
            else:
                last_page = 1
        film_rows = soup.select(".profile-content-item")
        for film_row in film_rows:
            film_name = str(film_row.select_one(".movie_title").text).strip()
            film_link = f"https://www.mafab.hu{str(film_row.select_one('.movie_title_link').get('href')).strip()}"
            film_rating = str(film_row.select_one(
                ".pci-movie-row-stars span").get("title")).strip()
            film_downloader = FilmDownloader(film_link, film_rating)
            films.get("films").append(film_downloader.get_film_data())
            download_films += 1
            print(
                f"\rLetöltött filmadatok a memóriába: {download_films}/{films_counter}", end="")
        if current_page == last_page:
            break
        else:
            current_page += 1
    else:
        print(
            f"Meghiúsúlt az oldalletöltés! Az utolsó sikeres oldal: {current_page}")
        break

try:
    json = dumps(films, ensure_ascii=False)
    json_file = open("films.json", "w", encoding="utf-8")
    json_file.write(json)
    json_file.close()
    input("\nA JSON fájl sikeresen elkészült.")
except:
    input("\nHiba történt a JSON fájl elkészítésekor!")
