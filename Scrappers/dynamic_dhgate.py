from Scrappers.dynamic_scrappers import DynamicScrapers
import re
import random
from lxml import etree

class DynamicDhgate(DynamicScrapers):

    BASE_URL = 'https://www.dhgate.com'
    SEARCH_URL = 'https://www.dhgate.com/wholesale/search.do'

    def search_value_page(self, value):
        params = {
            'act': 'search',
            'sus': ' ',
            'searchkey': value,
            'catalog': ' ',
        }
        response = self.request(self.SEARCH_URL, params=params)
        tree = etree.HTML(response.text)
        all_refs = tree.xpath('//*[@id="proGallery"]/div[2]/div[1]/div/div/div/h3/a/@href')
        val_refs =  all_refs[1:min(11, len(all_refs))]
        return [self.request('http:' + ref) for ref in val_refs]

    def search_value_weight(self, page):
        all_kg = []
        for one_page in page:
            all_kg += re.findall(r"(\d+|\d+\.\d+|\d+,\d+)? \( kg ", one_page.text.replace(',','').lower())
        all_kg = [float(i) for i in all_kg if float(i) != 0]
        kg_avg = sum(all_kg) / len(all_kg) if len(all_kg) else 1
        return [i for i in all_kg if i > kg_avg / 4 and i < kg_avg * 4]
