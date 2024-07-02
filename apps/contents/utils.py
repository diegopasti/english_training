import re
import json
import time
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

FAKE_AGENT = (
    "Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) "
    "AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5355d Safari/8536.25"
)


class SoundCloudError(Exception):
    def __init__(self, message, errors=None):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)

        # Now for your custom code...
        self.errors = errors


def get_paragraphs(content) -> list:

    elements = content.find_all("p")

    paragraphs = []
    for paragraph in elements[1:-2]:
        sub_paragraphs = paragraph.find_all("p")
        if sub_paragraphs:
            text = paragraph.text
            for item in sub_paragraphs:
                text = text.replace(item.text, "")
            paragraphs.append(text)

        else:
            paragraphs.append(paragraph.text)

    return paragraphs


def get_tracks_from_playlist(url: str) -> list:
    params = Request(url, headers={'User-Agent': FAKE_AGENT})
    request = urlopen(params)
    playlist = request.read().decode("utf-8").split("\n")

    tracks = []
    for element in playlist:
        if "https://cf-hls-media.sndcdn.com/media/" in element:
            tracks.append(element)

    return tracks


def get_tracks_from_notice(url: str) -> list:
    params = Request(url, headers={'User-Agent': FAKE_AGENT})
    request = urlopen(params)
    response = request.read().decode("utf-8")
    playlist_url = json.loads(response)["url"]
    return get_tracks_from_playlist(playlist_url)


def search_playlist_url_in_request_log(logs):

    playlist = None
    for item in logs:
        if "https://api-widget.soundcloud.com/media/soundcloud:tracks" in item["message"]:
            playlist = json.loads(item["message"])["message"]["params"]["request"]["url"]
            break

    return playlist


def get_audio(url: str, driver: webdriver.Chrome) -> list:
    driver.get(url)
    wait = WebDriverWait(driver, 5)
    button_that_enables_playlist = wait.until(
        EC.presence_of_element_located(
            (By.CLASS_NAME, "playButton")
        )
    )

    #clearing oldest logs
    driver.get_log("performance")

    ActionChains(driver).move_to_element(button_that_enables_playlist)
    button_that_enables_playlist.click()
    button_that_enables_playlist.click()
    logs = driver.get_log("performance")
    playlist_url = search_playlist_url_in_request_log(logs)
    tracks = get_tracks_from_notice(playlist_url)
    return tracks, playlist_url


def create_notice(url, driver):
    req = Request(url=url, headers={'User-Agent': 'Mozilla/5.0'})
    html_page = urlopen(req).read()
    bs = BeautifulSoup(html_page, features="html.parser")

    content = bs.find("div", class_="article")
    title_component = content.find("div", class_="article-title").find("h2").text

    pattern = "(.+) level (\\d)"
    title_parts = re.search(pattern, title_component)
    title = title_parts.group(1)[:-2]

    level = title_parts.group(2)

    text = content.find("div", id="nContent")
    publish_date = text.find("p").text

    paragraphs = get_paragraphs(text)

    total_paragraphs = 0
    total_sentences = 0
    total_words = 0

    elements = []

    for paragraph in paragraphs:
        sentences = []
        total_paragraphs += 1
        paragraph_sentences = paragraph.split(". ")
        total_sentences += len(paragraph_sentences)
        for sentence in paragraph_sentences:
            cleared_sentence = sentence.replace(", ", " , ").replace("; ", " ; ")
            words = cleared_sentence.split(" ")
            sentences.append({"sentece": sentence, "total_words": len(words), "words": words})
            total_words += len(words)
        elements.append(sentences)

    audio_url = content.find("div", class_="video-wrap").find("iframe")["data-ezsrc"]
    tracks, playlist = get_audio(audio_url, driver)

    notice = {
        "title": title,
        "level": level,
        "publish_date": publish_date,

        "body": {
            "text": "\n".join(paragraphs),
            "total_paragraphs": total_paragraphs,
            "total_sentences": total_sentences,
            "total_words": total_words,
            "elements": elements
        },
        "audio": {
            "source": audio_url,
            "playlist": playlist,
            "tracks": tracks,
        },
    }

    return notice


def import_notices(notices: list,  without_interface: bool = True):
    options = webdriver.ChromeOptions()

    # Chrome will start in Headless mode
    if without_interface:
        options.add_argument('headless')

    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    options.add_argument("--ignore-certificate-errors")
    driver = webdriver.Chrome(options=options)

    response = []
    for url in notices:
        notice = create_notice(url, driver)
        response.append(notice)

    driver.close()
    return response


if __name__ == "__main__":
    notices = [
        "https://www.newsinlevels.com/products/real-madrid-wins-champions-league-title-level-3",
        #"https://www.newsinlevels.com/products/europes-waste-goes-to-other-countries-level-1/",
        #"https://www.newsinlevels.com/products/mbappe-signs-a-deal-with-real-madrid-level-1/",
        #"https://www.newsinlevels.com/products/british-tv-presenter-is-missing-level-1/",
    ]

    print("English Trainging > Iniciando importação de noticias")
    response = import_notices(notices)
    print(response)
    print("English Training > Importação realizada com sucesso.")

