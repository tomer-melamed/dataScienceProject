from Scrappers.scrappers import Scrapers
from lxml import etree

class ScrapperTwo(Scrapers):

    BASE_URL = 'http://www.gutenberg.org'
    SEARCH_URL = 'http://www.gutenberg.org/ebooks/search/?sort_order=downloads'
    BOOKS_PER_PAGE = 25
    BOOKS_ITERS = 100

    def get_text(self):
        books_counter = 1
        all_books = []
        response = self.request(self.SEARCH_URL)
        tree = etree.HTML(response.text)
        all_books += tree.xpath('//*[@id="content"]/div[@class="body"]/div/ul/li/a/@href')[2:]
        books_counter += self.BOOKS_PER_PAGE
        for i in range(self.BOOKS_ITERS):
            response = self.request(self.SEARCH_URL + '&start_index=' + str(books_counter))
            tree = etree.HTML(response.text)
            all_books += tree.xpath('//*[@id="content"]/div[@class="body"]/div/ul/li/a/@href')[2:]
            books_counter += self.BOOKS_PER_PAGE
        all_ref = self.get_all_books_text_ref(all_books)
        print('Done with all refs')
        return self.get_all_books_text(all_ref)

    def get_all_books_text_ref(self, all_books):
        all_text_ref = []
        for book in all_books:
            response = self.request(self.BASE_URL + book)
            tree = etree.HTML(response.text)
            all_text_ref.append(tree.xpath('//*[@id="download"]/div/table/tr[@class="even"]/td[@property="dcterms:format"]/a/@href'))
            print(all_text_ref)
        self.delay(1/5)
        return all_text_ref

    def get_all_books_text(self, all_ref):
        all_text = []
        for refs in all_ref:
            for ref in refs:
                if 'h.htm' in ref:
                    print(ref)
                    response = self.request(self.BASE_URL + ref)
                    all_text.append(response.text)
        return all_text

    def get_name(self):
        return 'scraper_2'




# a = ScrapperTwo()
# a.get_text()
