import os
import re
import json

from urllib.request import Request, urlopen, urlretrieve
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from apps.core.utils.handlers.audio import merge_audios, split_audio
from apps.core.utils.handlers.files import delete_files
from main.settings import MEDIA_URL

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


class NoticesImporter:
    content = None
    paragraphs = None

    def __init__(self, driver):
        self.driver = driver
        self.content = None

        self.title = ""
        self.level = None
        self.publish_date = None
        self.text = None

        self.paragraphs = []
        self.elements = []

        self.audio = None
        self.phrases_audio = None

        self.audio_url = None
        self.playlist = None
        self.tracks = None

        self.total_paragraphs = 0
        self.phrases = 0
        self.words = 0

    def __get_content_from_notice(self, url):
        """
        Download notice page and save the part containing the text for processing.

        :param url: Url of the page containing the news.
        :return: Page element containing the body of the news.
        """

        request = Request(url=url, headers={'User-Agent': 'Mozilla/5.0'})
        html_page = urlopen(request).read()
        self.bs = BeautifulSoup(html_page, features="html.parser")
        return self.bs.find("div", class_="article")

    def __get_notice_metadata(self):
        """
        Search and return the news title, level, publish_date

        :return:
        """

        title_component = self.content.find("div", class_="article-title").find("h2").text

        pattern = "(.+) level (\\d)"
        title_parts = re.search(pattern, title_component)
        self.title = title_parts.group(1)[:-2]
        self.level = title_parts.group(2)

        self.text = self.content.find("div", id="nContent")
        self.publish_date = self.text.find("p").text

    def __get_paragraphs(self, text) -> list:
        """
        Split text in paragraphs.

        In some news articles there is a problem when delimiting paragraphs, meaning that subsequent
        paragraphs may appear within the first tag. So we check if there are subparagraphs and remove
        it from the original paragraph.
        """

        elements = text.find_all("p")

        for paragraph in elements[1:-2]:
            sub_paragraphs = paragraph.find_all("p")
            if sub_paragraphs:
                text = paragraph.text
                for item in sub_paragraphs:
                    text = text.replace(item.text, "")
                self.paragraphs.append(text)

            else:
                self.paragraphs.append(paragraph.text)

        return self.paragraphs

    def __get_elements(self):
        """
        Search and count phrases and words

        :return: List containing phrases and words present in the text

        """

        for paragraph in self.paragraphs:
            phrases = []
            paragraph_phrases = paragraph.split(". ")

            self.total_paragraphs += 1
            self.phrases += len(paragraph_phrases)

            count = 0
            for phrase in paragraph_phrases:
                cleared_phrase = phrase.replace(", ", " , ").replace("; ", " ; ")
                words = cleared_phrase.split(" ")

                phrases.append(
                    {
                        "phrase": phrase,
                        "audio": self.phrases_audio[count],
                        "total_words": len(words),
                        "words": words
                    }
                )
                self.words += len(words)
                count += 1
            self.elements.append(phrases)

        return self.elements

    def __get_tracks_from_playlist(self, url: str) -> list:
        """
        Download the playlist tracks containing the news audio

        :param url: Url of the playlist containing the files
        :return: The list with the url of the original tracks and the list with the path of the tracks by phrases
        """

        params = Request(url, headers={'User-Agent': FAKE_AGENT})
        request = urlopen(params)
        playlist = request.read().decode("utf-8").split("\n")

        tracks = []
        temporary_files = []
        count = 1

        for element in playlist:
            if "https://cf-hls-media.sndcdn.com/media/" in element:
                filename = os.path.join(MEDIA_URL, "temp", f"{count}.mp3")
                urlretrieve(element, filename)
                tracks.append(element)
                temporary_files.append(filename)
                count += 1

        publish_date_parts = self.publish_date[:10].split("-")
        date = f"{publish_date_parts[2]}{publish_date_parts[1]}{publish_date_parts[0]}"
        folder = os.path.join(MEDIA_URL, "notices", date)
        if not os.path.exists(folder):
            os.makedirs(folder)

        folder = os.path.join(folder, self.title.lower().replace(" ","_"))
        if not os.path.exists(folder):
            os.makedirs(folder)

        folder = os.path.join(folder, "tracks")
        if not os.path.exists(folder):
            os.makedirs(folder)

        self.audio = merge_audios(temporary_files, folder)
        delete_files(temporary_files)

        self.phrases_audio = split_audio(self.audio, folder)
        return tracks

    def __get_tracks_from_notice(self, url: str) -> list:
        """
        Search for the url containing the news audio playlist

        :param url: Playlist url
        :return: List of tracks of audio
        """

        params = Request(url, headers={'User-Agent': FAKE_AGENT})
        request = urlopen(params)
        response = request.read().decode("utf-8")
        playlist_url = json.loads(response)["url"]
        return self.__get_tracks_from_playlist(playlist_url)

    def __search_playlist_url_in_request_log(self, logs):
        """
        Search for the address containing the audio playlist

        :param logs: Website request log to identify the repository containing news audios
        :return: Url of the playlist containing the news tracks
        """

        playlist = None
        for item in logs:
            if "https://api-widget.soundcloud.com/media/soundcloud:tracks" in item["message"]:
                playlist = json.loads(item["message"])["message"]["params"]["request"]["url"]
                break

        return playlist

    def __get_audio(self, url: str, driver: webdriver.Chrome) -> (list, str):
        """
        Search and download the news audio

        :param url: News url
        :param driver: Webdrive used to make requests on the website
        :return: Returns playlist link and list of audios
        """

        driver.get(url)
        wait = WebDriverWait(driver, 5)
        button_that_enables_playlist = wait.until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "playButton")
            )
        )

        # clearing oldest logs
        driver.get_log("performance")

        ActionChains(driver).move_to_element(button_that_enables_playlist)
        button_that_enables_playlist.click()
        button_that_enables_playlist.click()
        logs = driver.get_log("performance")
        self.playlist = self.__search_playlist_url_in_request_log(logs)
        self.tracks = self.__get_tracks_from_notice(self.playlist)

    def __format_notice(self):
        """
        Prepares data for import containing news data and audio

        :return: Data dictionary representing the news
        """

        return {
            "level": self.level,
            "publish_date": self.publish_date,
            "title": self.title,
            "text": "\n".join(self.paragraphs),

            "audio": self.audio,

            "elements": self.elements,

            "counters": {
                "paragraphs": self.total_paragraphs,
                "phrases": self.phrases,
                "words": self.words,
            }
        }

    def import_notice(self, url: str):
        """
            Creates export file containing the data and audio of the requested news

            :param url: News url
            :return: News data and audio for import
            """

        self.content = self.__get_content_from_notice(url)
        self.__get_notice_metadata()
        self.paragraphs = self.__get_paragraphs(self.text)

        self.audio_url = self.content.find("div", class_="video-wrap").find("iframe")["data-ezsrc"]
        self.__get_audio(self.audio_url, self.driver)

        self.elements = self.__get_elements()

        return self.__format_notice()


def import_notices(notices: list, without_interface: bool = True):
    """
    Import news data and audio

    :param notices: List containing url of news that will be imported
    :param without_interface: Configuration to control the display of the request client interface.
                              By default, is True so the interface is not loaded to optimize resources.
    :return:
    """

    options = webdriver.ChromeOptions()

    # Chrome will start in Headless mode
    if without_interface:
        options.add_argument('headless')

    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    options.add_argument("--ignore-certificate-errors")
    driver = webdriver.Chrome(options=options)
    importer = NoticesImporter(driver)
    response = []
    for url in notices:
        notice = importer.import_notice(url)
        response.append(notice)

    driver.close()
    return response


if __name__ == "__main__":
    notices = [
        "https://www.newsinlevels.com/products/real-madrid-wins-champions-league-title-level-3",
        # "https://www.newsinlevels.com/products/europes-waste-goes-to-other-countries-level-1/",
        # "https://www.newsinlevels.com/products/mbappe-signs-a-deal-with-real-madrid-level-1/",
        # "https://www.newsinlevels.com/products/british-tv-presenter-is-missing-level-1/",
    ]

    print("English Trainging > Iniciando importação de noticias")
    response = import_notices(notices)
    print(response)
    print("English Training > Importação realizada com sucesso.")
