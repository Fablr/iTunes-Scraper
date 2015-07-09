__author__ = 'Chris Day'
__publisher__ = 'Fabler LLC'

from abc import ABCMeta, abstractmethod
from bs4 import BeautifulSoup
import requests
import string
import logging
import re
import time
import sys

CATEGORIES = {
    'arts': "https://itunes.apple.com/us/genre/podcasts-arts/id1301?",
    'business': "https://itunes.apple.com/us/genre/podcasts-business/id1321?",
    'comedy': "https://itunes.apple.com/us/genre/podcasts-comedy/id1303?",
    'education': "https://itunes.apple.com/us/genre/podcasts-education/id1304?",
    'games_and_hobbies': "https://itunes.apple.com/us/genre/podcasts-games-hobbies/id1323?",
    'government_and_organizations': "https://itunes.apple.com/us/genre/podcasts-government-organizations/id1325?",
    'health': "https://itunes.apple.com/us/genre/podcasts-health/id1307?",
    'kids_and_family': "https://itunes.apple.com/us/genre/podcasts-kids-family/id1305?",
    'music': "https://itunes.apple.com/us/genre/podcasts-music/id1310?",
    'news_and_politics': "https://itunes.apple.com/us/genre/podcasts-news-politics/id1311?",
    'religion_and_spirituality': "https://itunes.apple.com/us/genre/podcasts-religion-spirituality/id1314?",
    'science_and_medicine': "https://itunes.apple.com/us/genre/podcasts-science-medicine/id1315?",
    'society_and_culture': "https://itunes.apple.com/us/genre/podcasts-society-culture/id1324?",
    'sports_and_recreation': "https://itunes.apple.com/us/genre/podcasts-sports-recreation/id1316?",
    'tv_and_film': "https://itunes.apple.com/us/genre/podcasts-tv-film/id1309?",
    'technology': "https://itunes.apple.com/us/genre/podcasts-technology/id1318?"
    }

FORMULA = "&letter={0}&page={1}"
ITUNES = "https://itunes.apple.com/lookup?id={0}"

SECONDS_BETWEEN_REQUESTS = 0.5

class BaseScraper(metaclass=ABCMeta):
    def __init__(self, url):
        self.url = url
        self.children = []
        return

    def __iter__(self):
        self.iter = iter(self.children)
        return self.iter

    def next(self):
        return next(self.iter)

    @abstractmethod
    def scrape(self):
        pass

class CategoryScraper(BaseScraper):
    def __init__(self, url):
        super(CategoryScraper, self).__init__(url)
        return

    def scrape(self):
        for letter in string.ascii_uppercase[:26]:
            url = self.url + FORMULA.format(letter, 1)
            result = requests.get(url)

            if 200 != result.status_code:
                logging.warning("status code {0} from {1}".format(result.status_code, url))
                continue

            html = BeautifulSoup(result.content, "html.parser")
            pagination = html.find('ul', 'paginate')

            if pagination is None:
                size = 2
            else:
                size = len(pagination.find_all('li'))

            for page in range(1, size):
                self.children.append(self.url + FORMULA.format(letter, page))
        return


class PodcastScraper(BaseScraper):
    def __init__(self, url):
        super(PodcastScraper, self).__init__(url)
        return

    def scrape(self):
        page_result = requests.get(self.url)

        if 200 == page_result.status_code:
            html = BeautifulSoup(page_result.content, "html.parser")
            content = html.find(id="selectedcontent")

            if content is None:
                logging.error("unable to find content from {0}".format(self.url))
                raise IOError

            links = content.find_all('a')

            for link in links:
                podcast_url = link.attrs['href']
                match = re.findall('id(\d+)$', podcast_url)

                if match is None:
                    logging.warning("unable to parse id from {0}".format(podcast_url))
                    continue

                url = ITUNES.format(match[0])
                try:
                    api_result = requests.get(url)

                    if 200 != api_result.status_code:
                        logging.warning("status code {0} from {1}".format(api_result.status_code, url))
                        continue

                    json = api_result.json()

                    if 'resultCount' not in json or 'results' not in json:
                        logging.warning("no results from {0}".format(url))
                        continue

                    size = json['resultCount']

                    for i in range(0, size):
                        current = json['results'][i]

                        if 'feedUrl' not in current:
                            logging.warning("no feed in result {0} from {1}".format(i, url))
                            continue

                        feed_url = json['results'][i]['feedUrl']

                    #if isinstance(feed_url, str):
                    #    feed_url = feed_url.encode('UTF-8')

                        self.children.append(feed_url)
                except: 
                    print(url, "failed. Unexpected error: ", sys.exc_info()[0])
                    pass
        else:
            logging.warning("status code {0} from {1}".format(page_result.status_code, self.url))
        return

def store_feed(feed):
    f = open('feeds.txt', 'a')
    f.write(feed)
    f.write('\r\n')
    return

def async_main():
    pass

def serial_main():
    for category in CATEGORIES:
        category_scraper = CategoryScraper(CATEGORIES[category])
        category_scraper.scrape()

        for url in category_scraper:
            podcast_scraper = PodcastScraper(url)
            podcast_scraper.scrape()

            for feed in podcast_scraper:
                time.sleep(SECONDS_BETWEEN_REQUESTS)
                store_feed(feed)

            time.sleep(SECONDS_BETWEEN_REQUESTS)
    return

if __name__ == "__main__":
    serial_main()
