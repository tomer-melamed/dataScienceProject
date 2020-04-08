import db
import statistics
from matplotlib import pyplot as plt
import plotly.graph_objects as go
import numpy as np

class DataAnalyzing:

    VIOLIN_COLORS = ['red', 'blue', 'green']

    def __init__(self):
        self.db = db.Db()

    def _get_all_categories(self):
        get_categories_query = 'SELECT category, father_category, grandfather_category ' \
                               'FROM amazonproductsdata ' \
                               'GROUP BY category'
        return self.db.execute_query(get_categories_query)

    def _get_all_full_categories(self):
        q = 'SELECT category, father_category, grandfather_category ' \
            'FROM amazonproductsdata ' \
            'WHERE father_category IS NOT NULL AND grandfather_category IS NOT NULL ' \
            'GROUP BY category'
        return self.db.execute_query(q)

    def _add_advance_category_values_to_products(self, full_categories):
        for category in full_categories:
            base_category = category['category']
            father_category = category['father_category']
            grandfather_category = category['grandfather_category']
            q = f'UPDATE `amazonproductsdata` SET father_category = "{father_category}", grandfather_category = "{grandfather_category}" WHERE category = "{base_category}" AND father_category IS NULL AND grandfather_category IS NULL'
            self.db.execute_query(q)

    def _set_all_categories_summerized_data(self, caegories):
        for j in range(len(caegories)):
            base_category = caegories[j]['category']
            father_category = caegories[j]['father_category']
            grandfather_category = caegories[j]['grandfather_category']
            q = f'SELECT id, weight_kg, size_capacity, url FROM `amazonproductsdata` WHERE category = "{base_category}" AND father_category = "{father_category}" AND grandfather_category = "{grandfather_category}"'
            category_size_and_weight = self.db.execute_query(q)
            size_vec = [i['size_capacity'] for i in category_size_and_weight]
            weight_vec = [i['weight_kg'] for i in category_size_and_weight]
            weight_median = statistics.median(weight_vec)
            size_median = statistics.median(size_vec)
            if len(category_size_and_weight) > 5:
                self._set_product_data(category_size_and_weight, weight_median, size_median, base_category, father_category, grandfather_category)

    def _set_product_data(self, category_size_and_weight, weight_median, size_median, base_category, father_category, grandfather_category):
        weight_sum = 0
        size_sum = 0
        num_of_inliers = 0
        ids = ''
        all_weights = ''
        if weight_median > 1.5:
            weight_upper_bound = 2.5
            weight_lower_bound = 4
        elif weight_median < 0.75:
            weight_upper_bound = 4
            weight_lower_bound = 5
        else:
            weight_upper_bound = 3
            weight_lower_bound = 5
        f = open('outliers_log.txt', 'a')
        try:
            f.write(base_category + ' outliers url:\n')
        except:
            pass
        for i in category_size_and_weight:
            if i['weight_kg'] < weight_upper_bound * weight_median and i['weight_kg'] > weight_median / weight_lower_bound and \
                            i['size_capacity'] < 20 * size_median and i['size_capacity'] > size_median / 20:
                weight_sum += i['weight_kg']
                size_sum += i['size_capacity']
                ids += str(i['id']) + ','
                num_of_inliers += 1
            else:
                f.write('   ' + i['url'] + '\n')
            all_weights += str(i['weight_kg']) + ','
        f.close()
        weight_avg = weight_sum / max(num_of_inliers, 1)
        size_avg = size_sum / max(num_of_inliers, 1)
        q = f'INSERT INTO `categories_details` VALUES (NULL, "{grandfather_category}", "{father_category}", "{base_category}", {weight_median}, {size_median}, {weight_avg}, {size_avg}, "{ids}", "{all_weights}")'
        self.db.execute_query(q)

    def _get_weight_for_category(self, category, father_category, grandfather_category, inliers_ids):
        q = f"SELECT weight_kg FROM amazonproductsdata WHERE category = \"{category}\" and father_category = \"{father_category}\" and grandfather_category = \"{grandfather_category}\" AND id IN ({inliers_ids})"
        data = self.db.execute_query(q)
        return [i['weight_kg'] for i in data]


    def get_violin_plot_of_categorey(self, categories, father_categories, grandfather_categories):
        weights = []
        for i in range(len(categories)):
            inliers_ids = self._get_category_inliers(categories[i], father_categories[i], grandfather_categories[i])
            weights.append(self._get_weight_for_category(categories[i], father_categories[i], grandfather_categories[i], inliers_ids))
        fig, ax = plt.subplots()
        b = ax.violinplot(weights, showmeans=False, showmedians=True)
        j = 0
        for pc in b['bodies']:
            pc.set_facecolor(self.VIOLIN_COLORS[j])
            pc.set_edgecolor('black')
            j += 1
        ax.set_title('violin plot')
        ax.set_xlabel('category')
        ax.set_ylabel('weight')
        ax.set_xticks([1, 2, 3])
        ax.set_xticklabels(categories)
        ax.yaxis.grid(True)
        plt.show()

    def update_all_old_categories(self):
        full_categories = self._get_all_full_categories()
        self._add_advance_category_values_to_products(full_categories)

    def set_categories_details(self):
        full_categories = self._get_all_full_categories()
        self._set_all_categories_summerized_data(full_categories)

    def _get_category_inliers(self,category, father_category, grandfather_category):
        q = f'SELECT amazon_product_ids FROM categories_details WHERE category = "{category}" AND father_category = "{father_category}" AND grandfather_category = "{grandfather_category}"'
        inliers = self.db.execute_query(q)
        inliers_list = inliers[0]['amazon_product_ids']
        return inliers_list[:-1]

    def get_all_top_weight_ordered(self):
        q_asc = 'SELECT category, weight_average ' \
            'FROM `categories_details` ' \
            'ORDER BY weight_average ASC LIMIT 5'
        lowest_weight = self.db.execute_query(q_asc)
        lowest_weight_by_category = [i['category'] for i in lowest_weight]
        print('5 lowest categories by weight:')
        for i in lowest_weight_by_category:
            print('     ' + i)
        q_desc = 'SELECT category, weight_average ' \
            'FROM `categories_details` ' \
            'ORDER BY weight_average DESC LIMIT 5'
        highest_weight = self.db.execute_query(q_desc)
        highest_weight_by_category = [i['category'] for i in highest_weight]
        print('5 highest categories by weight:')
        for i in highest_weight_by_category:
            print('     ' + i)

    def get_all_top_sizes_ordered(self):
        q_asc = 'SELECT category, size_average ' \
            'FROM `categories_details` ' \
            'ORDER BY size_average ASC LIMIT 5'
        lowest_weight = self.db.execute_query(q_asc)
        lowest_weight_by_category = [i['category'] for i in lowest_weight]
        print('5 lowest categories by size:')
        for i in lowest_weight_by_category:
            print('     ' + i)
        q_desc = 'SELECT category, size_average ' \
            'FROM `categories_details` ' \
            'ORDER BY size_average DESC LIMIT 5'
        highest_weight = self.db.execute_query(q_desc)
        highest_weight_by_category = [i['category'] for i in highest_weight]
        print('5 highest categories by size:')
        for i in highest_weight_by_category:
            print('     ' + i)

    def bar_plot_generator(self, categories, father_categories, grandfather_categories):
        fig = go.Figure()
        for i in range(len(categories)):
            category = categories[i]
            father_category = father_categories[i]
            grandfather_category = grandfather_categories[i]
            category_weights = self._get_all_scraped_weights(category, father_category, grandfather_category)
            fig.add_trace(go.Box(
                y=category_weights,
                name=category,
                boxpoints='outliers'
            ))
        fig.update_layout(title_text="Categories outliers analysis")
        fig.show()

    def _get_all_scraped_weights(self, category, father_category, grandfather_category):
        q = f'SELECT all_weights FROM categories_details WHERE category = "{category}" AND father_category = "{father_category}" AND grandfather_category = "{grandfather_category}"'
        all_weights = self.db.execute_query(q)[0]['all_weights'][:-1]
        weights_arr = all_weights.split(',')
        return [float(i) for i in weights_arr]

    def compare_specific_path(self, father_category, grandfather_category):
        q = f'SELECT weight_average, category FROM categories_details WHERE father_category = "{father_category}" AND grandfather_category = "{grandfather_category}"'
        weight_avg_by_category = self.db.execute_query(q)
        x_title = []
        values = []
        weight_avg_by_category_sorted = {}
        for i in weight_avg_by_category:
            weight_avg_by_category_sorted[i['category']] = i['weight_average']
            # x_title.append(i['category'])
            # values.append(i['weight_average'])
        sorted_list = {k: v for k, v in sorted(weight_avg_by_category_sorted.items(), key=lambda item: item[1])}
        for i in sorted_list.keys():
            x_title.append(i)
            values.append(sorted_list[i])
        y_pos = np.arange(len(values))
        plt.barh(y_pos, values, color='green')
        plt.yticks(y_pos, x_title)
        plt.xlabel("Weight avg")
        plt.title(grandfather_category + ' ' + father_category + ' weight avg')
        plt.show()


a = DataAnalyzing()
# a.get_violin_plot_of_categorey(['Alarm Clocks', 'Baby Bath', 'Basketballs'], ['HOME DÉCOR', 'BABY AND TODDLER TOYS', "FAN SHOP"], ["Home & Kitchen", "Baby", "Sports & Outdoors"])
# a.update_all_old_categories()
# a.set_categories_details()
# a.get_all_top_weight_ordered()
# a.get_all_top_sizes_ordered()
# a.bar_plot_generator(['Wrestling', 'Sleep & Lounge', 'Basketball'], ['SHOES', 'SHOES', "SHOES"], ["Men's Fashion", "Men's Fashion", "Men's Fashion"])
a.compare_specific_path("HOME AUDIO", "Electronics")
