from Scrappers.dynamic_scrappers import DynamicScrapers
from lxml import etree
import re
import random

class DynamicBritanica(DynamicScrapers):

    BASE_SEARCH_URL = 'https://www.britannica.com/search?query='
    BASE_URL = 'https://www.britannica.com'

    def search_value_page(self, value):
        url = self.BASE_SEARCH_URL + value
        response = self.request(url)
        tree = etree.HTML(response.text)
        all_refs = tree.xpath('/html/body/main/div/div/div/div[@class="grid"]/div/div[@class="search-results"]/ul/li/a/@href')
        all_texts = [self.request(self.BASE_URL + ref_url) for ref_url in all_refs]
        return all_texts

    def search_value_weight(self, page):
        all_kg = []
        for one_page in page:
            all_kg += re.findall(r"(\d+|\d+\.\d+|\d+,\d+)? kg", one_page.text.replace(',','').lower())
            range_kg = re.findall(r"(\d+-\d+)? kg", one_page.text.lower())
            if range_kg:
                for one_range in range_kg:
                    range_separator = one_range.find('-')
                    start = one_range[:range_separator]
                    end = one_range[range_separator + 1:]
                    if end and start:
                        all_kg += random.sample(range(int(start), int(end)), 3)
        all_kg = [float(i) for i in all_kg if float(i) != 0]
        kg_avg = sum(all_kg) / len(all_kg) if len(all_kg) else 1
        return [i for i in all_kg if i > kg_avg / 4 and i < kg_avg * 4]

# a = DynamicBritanica()
# a.search_value_weight(a.search_value_page('lion'))
