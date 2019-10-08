from abc import ABC, abstractmethod
import requests
import time

class Scrapers(ABC):

    def __init__(self):
        self.session = requests.Session()
        http_adapter = requests.adapters.HTTPAdapter(max_retries=3)  # https://github.com/requests/requests/issues/4664
        self.session.mount('http://', http_adapter)


    def request(self, url, method='GET'):
        r = None

        if method == 'GET':
            r = self.session.get(url=url)
        return r

    def delay(self, seconds):
        time.sleep(seconds)

    @abstractmethod
    def get_text(self):
        pass

    @abstractmethod
    def get_name(self):
        pass
