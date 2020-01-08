from Scrappers.dynamic_britanica import DynamicBritanica
from Scrappers.dynamic_citizendium import DynamicCitizendium
from Scrappers.dynamic_infoplease import DynamicInfoplease
from Scrappers.dynamic_wiki import DynamicWiki
from Scrappers.dynamic_conservapedia import DynamicConservapedia
from Scrappers.dynamic_dhgate import DynamicDhgate
import matplotlib.pyplot as plt

class DynamicScrappersData:

    scrappers = [DynamicBritanica(), DynamicCitizendium(), DynamicInfoplease(), DynamicWiki(), DynamicConservapedia()]
    scrappers_for_no_match_cases = [DynamicDhgate()]

    def get_weights(self, values):
        kg_dict = {}
        for val in values:
            all_kg = []
            for scrapper in self.scrappers:
                scrapper_page = scrapper.search_value_page(val)
                all_kg += scrapper.search_value_weight(scrapper_page)
            if len(all_kg) < 3:
                for extra_scraper in self.scrappers_for_no_match_cases:
                    scrapper_page = extra_scraper.search_value_page(val)
                    all_kg += extra_scraper.search_value_weight(scrapper_page)
            kg_dict[val] = all_kg
        return kg_dict

    def normalized_weights(self, values_dict):
        weight_values = values_dict.values()
        max_weights = max(list(map(lambda x: len(x), weight_values)))
        for i in values_dict:
            if len(values_dict[i]):
                ratio = max_weights / len(values_dict[i])
                if ratio > 1:
                    values_dict[i] = values_dict[i] * int(ratio)
        return values_dict

    def plot_generated(self, values_dict, values):
        num = 0
        all_points_x = []
        all_points_y = []
        for i in values_dict:
            num += 1
            for j in values_dict[i]:
                if float(j) > 0:
                    all_points_y.append(float(j))
                    all_points_x.append(num)

        plt.hist2d(all_points_x, all_points_y, bins=len(all_points_y), normed=False, cmap='Greens')
        plt.xticks([i + 1 for i in range(len(values))], values)
        plt.title('Weight heat map')
        plt.xlabel('Values')
        plt.ylabel('Weight in KG')
        cb = plt.colorbar()
        cb.set_label('Incidence')
        plt.show()

a = DynamicScrappersData()
values = ['shoes', 'rat', 'salmon']
b = a.get_weights(values)
normalized = a.normalized_weights(b)
a.plot_generated(normalized, values)
