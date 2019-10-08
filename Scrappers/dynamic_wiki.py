from Scrappers.dynamic_scrappers import DynamicScrapers
import re
import random

class DynamicWiki(DynamicScrapers):

    BASE_URL = 'https://en.wikipedia.org/wiki/'

    def search_value_page(self, value):
        url = self.BASE_URL + value
        response = self.request(url)
        return response

    def search_value_weight(self, page):
        text = self.clear_text(page.text.lower())
        all_kg = re.findall(r"(\d+|\d+\.\d+|\d+,\d+)? kg", text)
        range_kg = re.findall(r"(\d+-\d+)? kg", page.text.lower())
        if range_kg:
            for one_range in range_kg:
                range_separator = one_range.find('-')
                start = one_range[:range_separator]
                end = one_range[range_separator + 1:]
                if end and start:
                    all_kg += random.sample(range(int(start), int(end)), 3)
        all_kg = [float(i) for i in all_kg if i and float(i) != 0]
        kg_avg = sum(all_kg) / len(all_kg) if len(all_kg) else 1
        return [i for i in all_kg if i > kg_avg / 4 and i < kg_avg * 4]

    def clear_text(self, text):
        no_nbsp = text.replace('&#160;', ' ')
        no_comma = no_nbsp.replace(',', '')
        return no_comma

# a = DynamicWiki()
# a.search_value_weight(a.search_value_page('lion'))
