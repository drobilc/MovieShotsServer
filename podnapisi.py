import requests
from bs4 import BeautifulSoup

class PodnapisiNet(object):

    def __init__(self):
        self.MAIN_URL = "https://www.podnapisi.net"
        self.ADVANCED_SEARCH_URL = self.MAIN_URL + "/subtitles/search/advanced"

        self.session = requests.Session()
    
    def parse_subtitles(self, response):
        subtitles = []
        html = BeautifulSoup(response, 'html.parser')
        rows = html.find_all('tr', {'class': 'subtitle-entry'})
        
        for row in rows:
            first_column = row.find('td')
            subtitle_name = first_column.find('a', recursive=False)
            subtitles.append({
                "name": subtitle_name.text.strip(),
                "url": self.MAIN_URL + subtitle_name['href'],
                "download_url": self.MAIN_URL + subtitle_name['href'] + "/download"
            })

        return subtitles
    
    def search(self, keywords, language="en"):
        search_parameters = {
            "keywords": keywords, 
            "year": "",
            "seasons": "",
            "episodes": "",
            "language": language
        }
        response = self.session.get(self.ADVANCED_SEARCH_URL, params=search_parameters)
        subtitles = self.parse_subtitles(response.text)
        return subtitles