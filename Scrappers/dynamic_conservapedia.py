from Scrappers.dynamic_scrappers import DynamicScrapers
import re
import random

class DynamicConservapedia(DynamicScrapers):

    BASE_URL = 'https://www.conservapedia.com/'

    def search_value_page(self, value):
        url = self.BASE_URL + value
        response = self.request(url)
        return response

    def search_value_weight(self, page):
        all_kg = re.findall(r"(\d+|\d+\.\d+|\d+,\d+)? kg", page.text.replace(',','').lower())
        range_kg = re.findall(r"(\d+-\d+)? kg", page.text.lower())
        if range_kg:
            for one_range in range_kg:
                range_separator = one_range.find('-')
                start = one_range[:range_separator]
                end = one_range[range_separator + 1:]
                all_kg += random.sample(range(int(start), int(end)), 3)
        all_kg = [float(i) for i in all_kg if float(i) != 0]
        kg_avg = sum(all_kg) / len(all_kg) if len(all_kg) else 1
        return [i for i in all_kg if i > kg_avg / 4 and i < kg_avg * 4]
