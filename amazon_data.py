import matplotlib.pyplot as plt
import db
import numpy as np

class AmazonData:

    def __init__(self):
        self.db = db.Db()

    def generate_product_weight_histogram(self, product_name):
        db_product_sizes = self.db.execute_query('SELECT weight_kg from amazonproductsData where category = "' + product_name + '";')
        if not len(db_product_sizes):
            return
        product_sizes = [i['weight_kg'] for i in db_product_sizes]
        plt.hist(product_sizes, facecolor='blue', edgecolor='black')
        plt.title(product_name + ' Weight histogram')
        plt.xlabel('Kg')
        plt.ylabel('Reps')
        plt.show()

    def get_all_product_category(self):
        all_categories = self.db.execute_query('SELECT category FROM amazonproductsData GROUP BY category')
        all_categories_array = [i['category'] for i in all_categories]
        return all_categories_array

    def get_size_to_weight_ratio(self):
        ratio_data = self.db.execute_query('SELECT category, AVG(size_capacity), AVG(weight_kg), AVG(size_capacity) / AVG(weight_kg) AS ratio, COUNT(category) AS samples '
                                           'FROM amazonproductsData '
                                           'GROUP BY category '
                                           'HAVING COUNT(category) > 5 AND ratio IS NOT NULL '
                                           'ORDER BY ratio DESC')
        print('products with the highest ratio between their size to their weight:')
        for i in range(5):
            print('     category: ' + ratio_data[i]['category'] + ', with ' + str(ratio_data[i]['samples']) + ' samples, got ratio of: ' + str(ratio_data[i]['ratio']))

        lowest_pos = len(ratio_data) - 1
        print('products with the lowest ratio between their size to their weight:')
        for i in range(5):
            print('     category: ' + ratio_data[lowest_pos - i]['category'] + ', with ' + str(ratio_data[lowest_pos - i]['samples']) + ' samples, got ratio of: ' + str(ratio_data[lowest_pos - i]['ratio']))

    def get_weight_variance_of_products(self):
        all_products_categories = self.get_all_product_category()
        data_dict = {}
        for product in all_products_categories:
            product_dict_weights = self.db.execute_query('SELECT weight_kg FROM amazonproductsData WHERE category = "' + product + '"')
            data_dict[product] = [i['weight_kg'] for i in product_dict_weights]
        all_products_var = [np.var(data_dict[product]) for product in all_products_categories]
        max_index = np.argmax(all_products_var)
        print('The category with the highest variance is: ' + all_products_categories[max_index] + ', with variance of: ' + str(all_products_var[max_index]))

a = AmazonData()
a.generate_product_weight_histogram('Snow Boots')