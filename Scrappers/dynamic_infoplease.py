from Scrappers.dynamic_scrappers import DynamicScrapers
from lxml import etree
import re
import random

class DynamicInfoplease(DynamicScrapers):

    BASE_URL = 'https://www.infoplease.com/search/'
    BASE_REF_URL = 'https://www.infoplease.com'

    def search_value_page(self, value):
        url = self.BASE_URL + value
        response = self.request(url)
        tree = etree.HTML(response.text)
        all_refs =  tree.xpath('/html/body/div[@class="dialog-off-canvas-main-canvas"]/div[@class="container "]/main/article/section/article/h2/a/@href')
        return [self.request(self.BASE_REF_URL + ref) for ref in all_refs]

    def search_value_weight(self, page):
        all_kg = []
        for one_page in page:
            all_kg += re.findall(r"(\d+|\d+\.\d+|\d+,\d+)? kg", one_page.text.replace(',','').lower())
            range_kg = re.findall(r"(\d+-\d+)? kg", one_page.text.lower())
            if range_kg:
                for one_range in range_kg:
                    if one_range:
                        range_separator = one_range.find('-')
                        start = one_range[:range_separator]
                        end = one_range[range_separator + 1:]
                        all_kg += random.sample(range(int(start), int(end)), 3)
        all_kg = [float(i) for i in all_kg if float(i) != 0]
        kg_avg = sum(all_kg) / len(all_kg) if len(all_kg) else 1
        return [i for i in all_kg if i > kg_avg / 4 and i < kg_avg * 4]

# a = DynamicInfoplease()
# a.search_value_weight(a.search_value_page('lion'))
