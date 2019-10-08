from Scrappers.scrappers import Scrapers
from lxml import etree


class ScrapperFour(Scrapers):

    BASE_SEARCH_URL = 'https://www.factmonster.com/search?page='
    BASE_URL = 'https://www.factmonster.com'
    PAGES_TO_SEARCH = 2500

    def get_text(self):
        all_refs = self.get_all_refs()
        print(all_refs)
        all_books = self.get_all_books(all_refs)
        return all_books

    def get_all_refs(self):
        all_refs = []
        for i in range(self.PAGES_TO_SEARCH):
            next_search_url = self.BASE_SEARCH_URL + str(i + 1)
            response = self.request(next_search_url)
            tree = etree.HTML(response.text)
            all_refs += tree.xpath('//*[@id="block-fm-content"]/article/h2/a/@href')
            print(tree.xpath('//*[@id="block-fm-content"]/article/h2/a/@href'))
        return all_refs

    def get_all_books(self, all_refs):
        all_texts = []
        for ref in all_refs:
            response = self.request(self.BASE_URL + ref)
            print(self.BASE_URL + ref)
            all_texts.append(response.text)
        return all_texts

    def get_name(self):
        return 'scraper_4'
