from Scrappers.scrappers import Scrapers
from lxml import etree


class ScrapperThree(Scrapers):

    BASE_SEARCH_URL = 'https://www.fulltextarchive.com/search//'
    BASE_URL = 'https://www.fulltextarchive.com'
    PAGES = 250

    def get_text(self):
        all_refs = self.get_all_refs()
        print(all_refs)
        all_books = self.get_all_books(all_refs)
        print(all_books)
        return self.get_all_texts(all_books)

    def get_all_refs(self):
        response = self.request(self.BASE_SEARCH_URL)
        tree = etree.HTML(response.text)
        all_refs = tree.xpath('//*[@id="results"]/dl/dt/a/@href')
        for i in range(self.PAGES):
            next_search_url = self.BASE_SEARCH_URL + str(i + 1) + '/7945/'
            response = self.request(next_search_url)
            tree = etree.HTML(response.text)
            all_refs += tree.xpath('//*[@id="results"]/dl/dt/a/@href')
        return all_refs

    def get_all_books(self, all_refs):
        all_books = []
        for ref in all_refs:
            response = self.request(self.BASE_URL + ref)
            tree = etree.HTML(response.text)
            try:
                all_books += tree.xpath('/html/body/ul/li/a/@href')
            except:
                all_books += ref
        return all_books

    def get_all_texts(self, all_books):
        all_texts = []
        for book in all_books:
            response = self.request(self.BASE_URL + book)
            all_texts.append(response.text)
            print(self.BASE_URL + book)
        return all_texts

    def get_name(self):
        return 'scraper_3'
