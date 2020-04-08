from nltk.corpus import wordnet
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
import db
import json
import re
from matplotlib import pyplot as plt
import numpy as np

class AmazonNlp:

    NO_MEANNING_WORDS = ['in']

    def __init__(self):
        self.db = db.Db()

    def get_best_matches(self):
        categories = self._get_all_categories()
        synsets = self._get_all_categories_synset(categories)
        self._get_all_categories_similarity(synsets)

    def _get_all_categories(self):
        q = "SELECT category, father_category, grandfather_category FROM categories_details"
        categories = self.db.execute_query(q)
        return categories

    def _get_all_categories_synset(self, categories):
        ps = PorterStemmer()
        synsets = {}
        for i in categories:
            synset = []
            words_synsets = []
            category_name = self._clear_category(i['category'])
            net = wordnet.synsets(category_name)
            if len(net):
                synset.append(net)
                words_synsets.append(ps.stem(word_tokenize(category_name)[0]))
            else:
                category_words = category_name.split()
                for word in category_words:
                    if word in self.NO_MEANNING_WORDS:
                        continue
                    net = wordnet.synsets(word)
                    if len(net):
                        synset.append(net)
                        words_synsets.append(ps.stem(word_tokenize(word)[0]))
            synsets[i['category']] = {'values': synset, 'synsets_words': words_synsets, 'father': i['father_category'],
                                      'grandfather': i['grandfather_category']}
        return synsets

    def _clear_category(self, name):
        name_no_and = name.replace('&', '')
        name_no_digits = re.sub('\d', '', name_no_and)
        return name_no_digits

    def _get_all_categories_similarity(self, synsets):
        similarity_dict = {i:{} for i in synsets.keys()}
        for i in synsets.keys():
            if not len(synsets[i]['values']):
                continue
            for j in synsets.keys():
                if not len(synsets[j]['values']) or i == j or j in similarity_dict[i]:
                    continue
                categories_sinilarity = self._similarity_calculator(synsets[j], synsets[i])
                similarity_dict[j][i] = categories_sinilarity
                similarity_dict[i][j] = categories_sinilarity
            print(i)
            self._set_results_to_db(similarity_dict[i], i)
        return similarity_dict

    def _similarity_calculator(self, category1_set, category2_set):
        scores = []
        num_of_sets = 0
        for counter1, ii in enumerate(category1_set['values']):
            score = 0
            same = True
            for counter2, jj in enumerate(category2_set['values']):
                if category1_set['synsets_words'][counter1] != category2_set['synsets_words'][counter2]:
                    same = False
                    cur_score = self._get_most_similar_synsets(ii, jj)
                    # for i in ii:
                    #     for j in jj:
                    #         cur_score = i.wup_similarity(j)
                    if cur_score:
                        score = max(score, cur_score)
                    if score == 1:
                        break
            if not same:
                num_of_sets += 1
                scores.append(score)
        scores_sorted = sorted(scores)[int(0.5 * num_of_sets) :]
        sum_scores = sum(scores_sorted)
        if category1_set['father'] == category2_set['father']:
            sum_scores += 0.001
        if category1_set['grandfather'] == category2_set['grandfather']:
            sum_scores += 0.0001
        return sum_scores / len(scores_sorted) if num_of_sets else 0

    def _get_most_similar_synsets(self, synset1, synset2):
        if len(synset1) == 1 and len(synset2) == 1:
            return synset1[0].wup_similarity(synset2[0])
        ps = PorterStemmer()
        best_score = 0
        best_synset = 0
        for i in synset1:
            definition1 = i.definition()
            def_words1 = definition1.split()
            def_synset1 = []
            for ii in def_words1:
                def_synset1 += wordnet.synsets(ps.stem(word_tokenize(ii)[0]))
            for j in synset2:
                for iii in def_synset1:
                    cur_score = iii.wup_similarity(j)
                    cur_score = cur_score if cur_score else 0
                    if cur_score > best_score:
                        best_score = cur_score
                        best_synset = i.wup_similarity(j)
        return best_synset


    def _set_results_to_db(self, similarity_object, category):
        dict_json = json.dumps(similarity_object).replace('"', '\\"')
        q = f'UPDATE categories_details SET similarity = "{dict_json}" WHERE category = "{category}"'
        self.db.execute_query(q)

    def _get_category_top_similarities(self, category, n=4):
        q = f'SELECT similarity FROM categories_details WHERE category = "{category}"'
        category_similarities = self.db.execute_query(q)[0]['similarity']
        json_format_similarities = json.loads(category_similarities)
        sorted_similarities = {k: v for k, v in sorted(json_format_similarities.items(), key=lambda item: item[1], reverse=True)}
        first_n_matches = ''
        for index, i in enumerate(sorted_similarities):
            if index >= n - 1:
                first_n_matches += '\'' + i + '\''
                return first_n_matches
            first_n_matches += '\'' + i + '\','
        return first_n_matches

    def subsize_category(self, category, n=4):
        matches = self._get_category_top_similarities(category, n)
        matches += ',\'' + category + '\''
        q = f'SELECT category, weight_median FROM categories_details WHERE category in ({matches}) ORDER BY weight_median ASC'
        selected_matches_weights = self.db.execute_query(q)
        order_by_weight_str = ''
        for i in selected_matches_weights:
            order_by_weight_str += i['category'] + ' =>'
        return order_by_weight_str[:-2], selected_matches_weights

    def visualize_results(self, results, base_category):
        categories = []
        weights = []
        for i in results:
            categories.append(i['category'])
            weights.append(i['weight_median'])
        plt.bar(np.arange(len(categories)), weights, align='center', alpha=0.5)
        plt.xticks(np.arange(len(categories)), categories)
        plt.ylabel('Weight')
        plt.title('Supersize Me plot of ' + base_category)
        plt.show()


a = AmazonNlp()
# a.get_best_matches()
category = '2 in 1 Laptops'
b = a.subsize_category(category, 4)
# print(b[0])
a.visualize_results(b[1], category)
