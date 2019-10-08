from abc import ABC, abstractmethod
import requests
import time

class DynamicScrapers(ABC):

    def __init__(self):
        self.session = requests.Session()
        http_adapter = requests.adapters.HTTPAdapter(max_retries=3)  # https://github.com/requests/requests/issues/4664
        self.session.mount('http://', http_adapter)


    def request(self, url, method='GET', params=None, headers=None):
        r = None

        if method == 'GET':
            r = self.session.get(url=url, params=params, headers=headers)
        return r

    def delay(self, seconds):
        time.sleep(seconds)

    @abstractmethod
    def search_value_page(self, value):
        pass

    @abstractmethod
    def search_value_weight(self, page):
        pass