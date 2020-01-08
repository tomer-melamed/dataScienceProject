from Scrappers.dynamic_scrappers import DynamicScrapers
from lxml import etree
import re
from db import Db
import time
import random


class AmazonScrapper(DynamicScrapers):

    BASE_URL = 'https://www.amazon.com/'
    BASE_SEARCH_URL = 'https://www.amazon.com/s/ref=nb_sb_noss'
    OUNCE_KILO = 0.0283495
    POUND_TO_KILO = 0.45359237
    WEIGHT_WORD_DESCRIPTION = ['light weight', 'too heavy', 'not heavy']

    def search_value_page(self, value):
        all_categories, categories_text =  self._get_categories()
        db = Db()
        for i in range(26, len(all_categories)):
            print(all_categories[i])
            self._searching_by_category(all_categories[i], db, categories_text[i])
            time.sleep(8)

    def search_value_weight(self, page):
        pass

    def _get_categories(self):
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9,he-IL;q=0.8,he;q=0.7',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'referer': self.BASE_URL,
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
        }
        base_page = self.request(self.BASE_URL, headers=headers)
        tree = etree.HTML(base_page.text)
        categories = tree.xpath('/html/body/div[@id="a-page"]/header/div/div[@id="nav-belt"]/div[@class="nav-fill"]/div/'
                                'form/div[@class="nav-left"]/div/div/select/option/text()')
        searches_url = tree.xpath('/html/body/div[@id="a-page"]/header/div/div[@id="nav-belt"]/div[@class="nav-fill"]/div/'
                                'form/div[@class="nav-left"]/div/div/select/option/@value')
        searches_text = tree.xpath('/html/body/div[@id="a-page"]/header/div/div[@id="nav-belt"]/div[@class="nav-fill"]/div/'
                                'form/div[@class="nav-left"]/div/div/select/option/text()')
        return searches_url, searches_text

    def _searching_by_category(self, category_url, db, category):
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9,he-IL;q=0.8,he;q=0.7',
            'referer': self.BASE_URL,
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
        }
        parameters = {
            'url': category_url,
            'field-keywords': '',
        }
        search_page = self.request(self.BASE_SEARCH_URL, headers=headers, params=parameters)
        tree = etree.HTML(search_page.text)
        all_inner_categories = tree.xpath('/html/body/div[@id="a-page"]/div[@class="a-fixed-left-flipped-grid s-padding-left-small s-padding-right-small s-span-page a-spacing-top-small"]'
                                          '/div/div[@class="a-fixed-left-grid-col a-col-right"]/div/div[@id="merchandised-content"]/'
                                          'div[contains(@id, "category")]/div/div/div/a/@href')
        all_inner_categories_text = tree.xpath('/html/body/div[@id="a-page"]/div[@class="a-fixed-left-flipped-grid s-padding-left-small s-padding-right-small s-span-page a-spacing-top-small"]'
                                          '/div/div[@class="a-fixed-left-grid-col a-col-right"]/div/div[@id="merchandised-content"]/'
                                          'div[contains(@id, "category")]/div/div/div/a/div/span/text()')
        special_case = False
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! only once!!!!!!!
        if category_url == 'search-alias=toys-and-games-intl-ship':
            all_inner_categories = all_inner_categories[9:]
            special_case = True
        for i in range(len(all_inner_categories)):
            print(all_inner_categories[i])
            self._get_all_items_url(all_inner_categories[i], db, all_inner_categories_text[i].strip(), category, special_case)
            time.sleep(5)
            special_case = False

    def _get_all_items_url(self, page_url, db, inner_category, category, special_case=False):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.9,he-IL;q=0.8,he;q=0.7',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
        }
        response = self.request('https://www.amazon.com' + page_url, headers=headers)
        tree = etree.HTML(response.text)
        products_url = tree.xpath('//*[@id="search"]/div[@class="s-desktop-width-max s-desktop-content sg-row"]/div[2]/'
                                  'div/span[4]/div[@class="s-result-list s-search-results sg-row"]/div/div/span/div/div/'
                                  'div[@class="sg-row"]/div[1]/div/div/span/a/@href')
        for i in range(0, 20):
            tree = etree.HTML(response.text)
            next_page_url = tree.xpath('//*[@id="search"]/div[1]/div[2]/div/span[@class="rush-component"]/div/span/div/div/ul/li[@class="a-last"]/a/@href')

            page_2_headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'en-US,en;q=0.9,he-IL;q=0.8,he;q=0.7',
                'referer': response.url,
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-user': '?1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
            }
            try:
                response = self.request('https://www.amazon.com' + next_page_url[0], headers=page_2_headers)
                tree = etree.HTML(response.text)
                products_url += tree.xpath('/html/body/div[1]/div[1]/div[1]/div[2]/div/span[4]/div[1]/div/div/span/div/div/span/a/@href')
            except:
                products_url = products_url
            time.sleep(random.randint(1, 7))
        if special_case:
            print('special case!!!!!!!!!')
            products_url = products_url[80:]
        for product_url in products_url[int(len(products_url) / 2):]:
            time.sleep(random.randint(4, 11))
            self._get_product_details(product_url, db, inner_category, category)

    def _get_product_details(self, product_url, db, inner_category, grandfather_category):
        weight = ''
        size = None
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.9,he-IL;q=0.8,he;q=0.7',
            'sec-fetch-site': 'none',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
        }
        product_page = self.request('https://www.amazon.com/' + product_url, headers=headers)
        print('https://www.amazon.com/' + product_url)
        tree = etree.HTML(product_page.text)
        title = tree.xpath('/html/body/div[@id="a-page"]/div[@id="dp"]/div[@id="dp-container"]/div[@id="ppd"]/div[@id="centerCol"]/div[@id="title_feature_div"]/div/h1/span/text()')
        if not len(title):
            title = tree.xpath('/html/body/div[@id="a-page"]/div[@id="dp"]/div[@id="dp-container"]/div[@id="ppd"]/div[@class="a-row"]/'
                               'div[@class="a-column a-span8 dp_aib_right_column_t2 a-span-last"]/div/div/div[@id="centerCol"]/'
                               'div[@id="titleBlock"]/div[@id="titleBlockRightSection"]/div[@id="title_feature_div"]/div/h1/span/text()')
        if not len(title):
            title = tree.xpath('/html/body/div[@id="a-page"]/div[@id="dp"]/div[@id="dp-container"]/div[@id="ppd-top"]/'
                               'div[@id="titleLayer"]/div/div[@id="titleBar-left"]/div[@id="superLeafTitleFeatureGroup"]/'
                               'div[@id="title_feature_div"]/div/h1/span/text()')
        if not len(title):
            title = tree.xpath('//*[@id="productTitle"]/text()')

        table = tree.xpath('/html/body/div[@id="a-page"]/div[@id="dp"]/div[@id="dp-container"]/div[@id="product-details-grid_feature_div"]/'
                           'div/div/div/div/div/div/div[@class="a-column a-span6"]/div[@class="a-row a-spacing-base"]/div/div[2]/div/div/'
                           'table')

        if len(table):
            try:
                weight = table[0].xpath('tr[2]/td/text()')[0]
                size = table[0].xpath('tr[3]/td/text()')[0]
            except:
                table = []

        if not len(table):
            table = tree.xpath('//*[@id="detail-bullets"]/table/tr/td')
            if len(table):
                try:
                    weight = table[0].xpath('div[@class="content"]/ul/li[1]/text()')[0]
                    size = table[0].xpath('div[@class="content"]/ul/li[1]/text()')[0]
                except:
                    table = []
        if not len(table):
            table = tree.xpath('//*[@id="productDetails_techSpec_section_1"]')
            if len(table):
                titles = table[0].xpath('tr/th/text()')
                descriptions = table[0].xpath('tr/td/text()')
                for i in range(len(titles)):
                    if 'item weight' in titles[i].lower():
                        weight = descriptions[i]
                    if 'product dimensions' in titles[i].lower() or 'package dimensions' in titles[i].lower():
                        size = descriptions[i]
        if not len(table):
            try:
                size_container = product_page.text.lower().find('product dimensions')
                size_container = size_container if size_container > -1 else product_page.text.lower().find('package dimensions')
                size = re.findall(r"(\d+\.\d+ x \d+\.\d+ x \d+\.\d+ inches|\d+\.\d+ x \d+ x \d+\.\d+ inches|\d+ x \d+\.\d+ x \d+\.\d+ inches|\d+\.\d+ x \d+\.\d+ x \d+ inches|\d+ x \d+ x \d+\.\d+ inches|\d+ x \d+\.\d+ x \d+ inches|\d+\.\d+ x \d+ x \d+ inches|\d+ x \d+ x \d+ inches)", product_page.text.lower()[size_container:])[0]
            except:
                return
            weight_idx = product_page.text.lower().find('item weight')
            weight_idx = weight_idx if weight_idx != -1 else product_page.text.lower().find('shipping weight')
            if not weight_idx:
                return
            weight = product_page.text[weight_idx: weight_idx + 250]
        try:
            product_specific_category = tree.xpath('/html/body/div[@id="a-page"]/div[@id="dp"]/div[@id="wayfinding-breadcrumbs_container"]/'
                                                   'div/ul/li/span/a/text()')[-1]
        except:
            product_specific_category = ''
        if not size:
            return
        id = self._get_id_from_url(product_url)
        title = title[0].strip().replace('"', r'\"') if len(title) else None
        weight_kg = self._get_weight_from_str(weight)
        size_capacity = self._get_size_from_str(size)
        category = product_specific_category.strip()
        # html = product_page.text.replace('"', r'\"')
        # html = html.replace('\\"', '')
        weight = weight.replace('"', r'\"')
        weight = weight.replace('\\"', '')
        url = product_page.url
        size = size.replace('"', r'\"')
        weight_descriptions = self._get_weight_reviews(product_page.text)
        if title and weight_kg != None and size_capacity != None and category:
            try:
                print(title)
                db.execute_query(f'INSERT INTO amazonproductsdata VALUES (NULL, "{title}", "{url}", {weight_kg}, "{category}", "{inner_category}", "{grandfather_category}", {size_capacity}, "", "{size}", "{weight}", "{weight_descriptions}")')
            except:
                try:
                    db.execute_query(f"INSERT INTO amazonproductsdata VALUES (NULL, '{title}', '{url}', {weight_kg}, '{category}', '{inner_category}', '{grandfather_category}', {size_capacity}, ``, '{size}', '{weight}', '{weight_descriptions}')")
                except:
                    print(title)
                    print(size_capacity)
                    print(weight_kg)
                    print(category)
                    return
        else:
            print(title)
            print(size_capacity)
            print(weight_kg)
            print(category)

    def _get_weight_from_str(self, string):
        ounces = re.findall(r"(\d+|\d+\.\d+) ounces", string.lower())
        if len(ounces):
            return float(ounces[0]) * self.OUNCE_KILO
        lbs_weight = re.findall(r"(\d+|\d+\.\d+) lbs", string.lower())
        if len(lbs_weight):
            return float(lbs_weight[0]) * self.POUND_TO_KILO
        pounds = re.findall(r"(\d+|\d+\.\d+) pounds", string.lower())
        return float(pounds[0]) * self.POUND_TO_KILO if len(pounds) else None

    def _get_size_from_str(self, string):
        two_edges = re.findall(r"(\d+|\d+\.\d+) x", string.lower())
        last_edge = re.findall(r"(\d+|\d+\.\d+) inches", string.lower())
        if len(two_edges) > 1 and len(last_edge):
            return float(two_edges[0]) * float(two_edges[1]) * float(last_edge[0])
        return None

    def _get_id_from_url(self, url):
        beg_idx = url.find('/dp/') + 4
        end_idx = url.find('/ref=')
        return url[beg_idx: end_idx]

    def _get_weight_reviews(self, text):
        weight_descriptions = ''
        start_reviews_index = text.lower().find('top reviews')
        end_reviews_index = text.lower().find('more to consider')
        if start_reviews_index < end_reviews_index:
            for i in self.WEIGHT_WORD_DESCRIPTION:
                if i in text.lower():
                    weight_descriptions += i + '|'
        return weight_descriptions



a = AmazonScrapper()
b = a.search_value_page('')
