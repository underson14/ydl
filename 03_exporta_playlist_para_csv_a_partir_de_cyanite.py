import csv
import logging
import os
import re
import spotipy
import spotipy.util as util
import sys
import time
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from spotipy.oauth2 import SpotifyClientCredentials
from tqdm import tqdm
from pathlib import Path

try:
    os.remove("/Volumes/Arquivos/Codigo/Spotify/temp/.cache")
    print("Arquivo .cache removido com sucesso!")
except FileNotFoundError:
    print("O arquivo .cache não existe. Nada foi feito.")

Path.cwd()
os.chdir('/Volumes/Arquivos/Codigo/Spotify/temp')
Path.cwd()

# Adicione suas credenciais do Spotify API
spotify_client_id = "4c549ec1159e4266a0cd8c187d417457"
spotify_client_secret = "aea8c20a17b047ffa1dcf4e420c19025"
SCOPE = "playlist-modify-public"
USERNAME = "underson14@gmail.com"

email = "yfq79089"
password = "cy20122014"

# Configure a autenticação do cliente
client_credentials_manager = SpotifyClientCredentials(
    client_id=spotify_client_id, client_secret=spotify_client_secret
)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Funções e código do Selenium/Web Scraping (incluir funções login, get_track_data e get_emotion)
logging.getLogger("spotipy").setLevel(logging.WARNING)


def login(driver, email, password):
    driver.get("https://app.cyanite.ai/login")

    WebDriverWait(driver, 3).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "input[type='text']"))
    )

    email_field = driver.find_element(By.CSS_SELECTOR, "input[type='text']")
    email_field.send_keys(email)

    password_field = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
    password_field.send_keys(password)

    login_button = driver.find_element(By.CSS_SELECTOR, "button[class='css-9iyjpt']")
    login_button.click()


def format_value(value, prefix):
    return f"{prefix}{value:.2f}"


def get_track_data(driver, url, source_id):
    driver.get(url)

    try:
        WebDriverWait(driver, 3).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, ".rs-table-cell-content")
            )
        )
    except TimeoutException:
        print("A tabela não foi carregada a tempo. Retornando None.")
        return None

    no_preview_selector = (
        ".rs-table-loader-wrapper .rs-table-loader .rs-table-loader-text"
    )
    no_preview_element = driver.find_elements(By.CSS_SELECTOR, no_preview_selector)

    if (
        no_preview_element
        and no_preview_element[0].text
        == "Spotify is not providing a preview of that song. Please try another."
    ):
        print("Spotify não está fornecendo uma prévia dessa música. Pulando.")
        return None

    show_all_button_css_selector = "div[aria-rowcount='2'] div[aria-colindex='17'] div.rs-table-cell-content button"

    max_attempts = 2
    attempt = 0

    while attempt < max_attempts:
        try:
            show_all_button = WebDriverWait(driver, 4).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, show_all_button_css_selector)
                )
            )
            driver.execute_script("arguments[0].click();", show_all_button)
            break
        except TimeoutException:
            attempt += 1
            if attempt == max_attempts:
                print("O botão 'Show all' não foi encontrado. Retornando None.")
                return None
            else:
                print(
                    "O botão 'Show all' não foi encontrado na primeira tentativa. Aguardando 10 segundos e tentando novamente."
                )
                time.sleep(10)

    try:
        dialog = WebDriverWait(driver, 3).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".css-1rtnuog"))
        )
    except TimeoutException:
        print(
            "A caixa de diálogo com os valores das médias de movimento não foi encontrada. Retornando None."
        )
        return None

    movement_data = {}

    movements = [
        "Pulsing",
        "Driving",
        "Stomping",
        "Running",
        "Robotic",
        "Groovy",
        "Bouncy",
        "Flowing",
        "Nonrhythmic",
        "Steady",
    ]
    movement_elements = dialog.find_elements(By.CSS_SELECTOR, ".css-1aqb3ik")

    for element in movement_elements:
        try:
            movement_name = element.text.split()[0]
            movement_value = round(float(element.text.split()[-1]) * 10)
            movement_data[movement_name] = "{:02}".format(movement_value)
        except IndexError:
            print(f"{source_id} - Erro ao processar o movimento {element.text}")

    return {
        "source_id": source_id,
        "Pul": movement_data.get("Pulsing"),
        "Drv": movement_data.get("Driving"),
        "Stm": movement_data.get("Stomping"),
        "Run": movement_data.get("Running"),
        "Rbt": movement_data.get("Robotic"),
        "Grv": movement_data.get("Groovy"),
        "Bnc": movement_data.get("Bouncy"),
        "Flw": movement_data.get("Flowing"),
        "Nnr": movement_data.get("Nonrhythmic"),
        "Std": movement_data.get("Steady"),
    }


def is_valid_url(url):
    regex = re.compile(
        r"^(https://open\.spotify\.com/playlist/)?[0-9a-zA-Z]{22}(\?si=.+)?$"
    )
    return re.match(regex, url) is not None


def get_track_ids_from_playlist(playlist_url):
    track_ids = []
    playlist_id = playlist_url.split("/")[-1].split("?")[0]
    if ":" in playlist_id:
        playlist_id = playlist_id.split(":")[1]

    playlist_info = sp.playlist(playlist_id)
    playlist_name = playlist_info["name"]

    # Adicionado paginação para obter todas as músicas da playlist
    offset = 0
    limit = 100

    while True:
        results = sp.playlist_tracks(playlist_id, offset=offset, limit=limit)

        if not results["items"]:
            break

        for item in results["items"]:
            track = item["track"]
            track_ids.append(track["id"])

        offset += limit

    return playlist_name, track_ids


def get_track_info(track_id):
    track = sp.track(track_id)
    artist_name = track["artists"][0]["name"]
    track_name = track["name"]
    popularity = track["popularity"]
    popularity = round(popularity / 10)
    formatted_popularity = (
        f"Pop {popularity:02d}" if popularity < 10 else f"Pop {popularity}"
    )
    track_url = track["external_urls"]["spotify"]
    isrc = track["external_ids"].get("isrc", "N/A")
    release_date = track["album"]["release_date"]

    # Verificar e ajustar o release_date
    if len(release_date) == 4:  # Apenas o ano está presente
        release_date = f"{release_date}-03-05"

    return {
        "artist_name": artist_name,
        "track_name": track_name,
        "formatted_popularity": formatted_popularity,
        "track_id": track_id,
        "track_url": track_url,
        "isrc": isrc,
        "release_date": release_date,
    }


def get_track_info_with_index(index, source_id):
    track_info = get_track_info(source_id)
    return index, track_info


# Opção para escolher a fonte das IDs das músicas
print("Selecione a fonte das IDs das músicas:")
print("1. Arquivo de texto")
print("2. Playlist do Spotify")

option = int(input("Digite o número da opção escolhida: "))

if option == 1:
    file_path = "/Volumes/Arquivos/Codigo/input.txt"
    with open(file_path, "r") as file:
        music_ids = [line.strip() for line in file.readlines()]
if option == 2:
    playlist_url = input("Digite a URL da playlist do Spotify: ")

    if is_valid_url(playlist_url):
        if not playlist_url.startswith("https://open.spotify.com/playlist/"):
            playlist_url = f"https://open.spotify.com/playlist/{playlist_url}"

        playlist_name, music_ids = get_track_ids_from_playlist(playlist_url)
        csv_path = f"/Volumes/Arquivos/Codigo/csv/Cyanite/{playlist_name}_cyanite.csv"
    else:
        print("URL inválida. Por favor, insira uma URL válida da playlist do Spotify.")
        sys.exit(1)
else:
    print("Opção inválida.")
    sys.exit(1)


track_info_list = [None] * len(music_ids)

with ThreadPoolExecutor() as executor:
    futures = {
        executor.submit(get_track_info_with_index, index, source_id): (index, source_id)
        for index, source_id in enumerate(music_ids, start=1)
    }
    for future in tqdm(as_completed(futures), total=len(music_ids)):
        index, track_info = future.result()
        track_info_list[index - 1] = track_info

print(
    "Todas as informações do spotify foram obtidas."
)  # Mensagem de aviso após a conclusão do laço

# Inicializar o WebDriver depois de escolher a opção

geckodriver_path = "/Volumes/Arquivos/Codigo/Spotify/geckodriver"

firefox_options = webdriver.FirefoxOptions()
firefox_options.add_argument(
    "--headless"
)  # Adicione esta linha para executar o navegador no modo headless.
firefox_options.add_argument("--disable-application-cache")
firefox_options.add_argument("--disable-images")
firefox_options.add_argument("--window-size=800x600")
# Exemplo: firefox_options.add_argument("--window-size=800x600")

driver = webdriver.Firefox(
    service=FirefoxService(executable_path=geckodriver_path), options=firefox_options
)

# Realize o login no site
login(driver, email, password)

# Verifique se o login foi bem-sucedido
WebDriverWait(driver, 5).until(EC.url_changes("https://app.cyanite.ai/login"))

if driver.current_url == "https://app.cyanite.ai/library":
    print("Login realizado com sucesso!")
else:
    print("Falha no login.")
    driver.quit()
    sys.exit(1)

movements = ["Bnc", "Drv", "Flw", "Grv", "Nnr", "Pul", "Rbt", "Run", "Stm", "Std"]
header = [
    "Index",
    "Artist Name",
    "Track Name",
    "Popularity",
    "Track ID",
    "Track URL",
    "ISRC",
    "Release Date",
] + movements


# Segundo laço: obtenha dados dos movimentos
track_data_list = []
for source_id in tqdm(music_ids, total=len(music_ids)):
    url = f"https://app.cyanite.ai/search?source=spotify&sourceId={source_id}&sourceUserLibraryId"
    track_data = get_track_data(driver, url, source_id)
    track_data_list.append(track_data)
print(
    "Todas as informações de cyanite.ai foram obtidas."
)  # Mensagem de aviso após a conclusão do laço

# Terceiro laço: combine informações da faixa e dados dos movimentos, e escreva no arquivo CSV
header = [
    "Index",
    "Artist Name",
    "Track Name",
    "Popularity",
    "Track ID",
    "Track URL",
    "ISRC",
    "Release Date",
] + movements
if not os.path.exists(csv_path):
    with open(csv_path, mode="w", newline="", encoding="utf-8") as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(header)

for index, (track_info, track_data) in enumerate(
    zip(track_info_list, track_data_list), start=1
):
    movement_values = []
    for movement in movements:
        abbr = movement[:3]
        value = (
            f"{abbr} {track_data[abbr]}" if track_data and track_data[abbr] else "N/A"
        )
        movement_values.append(value)

    with open(csv_path, mode="a", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(
            [
                index,
                track_info["artist_name"],
                track_info["track_name"],
                track_info["formatted_popularity"],
                track_info["track_id"],
                track_info["track_url"],
                track_info["isrc"],
                track_info["release_date"],
            ]
            + movement_values
        )
os.remove('/Volumes/Arquivos/Codigo/Spotify/temp/.cache')

print(f"A Playlist -{playlist_name}- foi exportada para {playlist_name}_cyanite.csv")


