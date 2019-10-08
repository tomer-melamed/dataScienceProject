from Scrappers.scrapper_one import ScrapperOne
from Scrappers.scrapper_two import ScrapperTwo
from Scrappers.scrapper_three import ScrapperThree
from Scrappers.scrapper_four import ScrapperFour
import json
import re


class ScrappersData:

    scrapers = [ScrapperFour]

    def get_data(self):
        all_texts = {}
        for scrapper in self.scrapers:
            scrapper_class = scrapper()
            all_texts[scrapper_class.get_name()] = scrapper_class.get_text()
        with open('data_4.txt', 'w') as outfile:
            json.dump(all_texts, outfile)

    def get_word_sentences(self, word, file_name):
        file = open(file_name, 'r')
        reader = file.read()
        while word in reader:
            pos = reader.find(word)
            print(reader[pos - 60: pos + 80])
            print('')
            reader = reader[pos + len(word):]

    def make_data_correct(self, file_name, file_to_write):
        file = open(file_name, 'r')
        reader = file.read()
        reader_no_br = reader.replace('<br', '')
        reader_no_comments = reader_no_br.replace('/>', '')
        reader_no_p = reader_no_comments.replace('</p>', '')
        reader_no_p_2 = reader_no_p.replace('<p>', '')
        reader_no_r = reader_no_p_2.replace('\\r', '')
        reader_no_n = reader_no_r.replace('\\n', '')
        reader_no_double_slash = reader_no_n.replace('\\', '')
        reader_no_i = reader_no_double_slash.replace('<i>', '')
        reader_no_i_2 = reader_no_i.replace('</i>', '')
        reader_no_i_3 = reader_no_i_2.replace('<i', '')
        reader_no_b = reader_no_i_3.replace('<b', '')
        reader_no_p = reader_no_b.replace('<p', '')
        reader_no_t = reader_no_p.replace('ttttt', '')
        with open(file_to_write, 'w') as outfile:
            json.dump(reader_no_t, outfile)


a = ScrappersData()
# a.get_data()
a.get_word_sentences(' cm', 'data_4.txt')


# a.make_data_correct('data_4.txt', 'data_4.txt')
