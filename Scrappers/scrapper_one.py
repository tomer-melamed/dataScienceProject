from Scrappers.scrappers import Scrapers
from lxml import etree

class ScrapperOne(Scrapers):

    BASE_URL = 'http://www.fullbooks.com'
    MAX_REQUESTS = 100

    def get_text(self):
        response = self.request(url=self.BASE_URL)
        tree = etree.HTML(response.text)
        refrences = tree.xpath('/html/body/div/table[2]/tr[1]/td[@width="50%"]/ul/li/font/a/@href')
        refrences += tree.xpath('/html/body/div/table[2]/tr[1]/td[@width="50%"]/font/ul/li/a/@href')
        all_books = self.get_books(refrences)
        all_parts = self.get_all_parts(all_books)
        return self.get_text_from_parts(all_parts)


    def get_books(self, refrences):
        all_books = []
        for url in refrences:
            response = self.request(self.BASE_URL + '/' + url)
            tree = etree.HTML(response.text)
            books_ref = tree.xpath('/html/body/div/table/tr/td/font/ul/li/a/@href')
            all_books += books_ref
        return all_books

    def get_all_parts(self, all_books):
        all_parts = []
        request_counter = 0
        try:
            for book in all_books:
                if request_counter > self.MAX_REQUESTS:
                    return all_parts
                request_counter += 1
                response = self.request(self.BASE_URL + '/' + book)
                tree = etree.HTML(response.text)
                try:
                    book_parts = tree.xpath('/html/body/div/table/tr/td/font/ul/li/a/@href')
                except:
                    book_parts = book
                self.delay(1/5)
                all_parts += book_parts
        except:
            return all_parts
        return all_parts

    def get_text_from_parts(self, all_parts):
        all_texts = []
        for part in all_parts:
            response = self.request(self.BASE_URL + '/' + part)
            all_texts.append(response.text)
        return all_texts

    def get_name(self):
        return 'scraper_1'

# a = ScrapperOne()
# a.get_text()
