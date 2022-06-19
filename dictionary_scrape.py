import csv
import requests
from bs4 import BeautifulSoup
from time import sleep
import argparse
import random
import re

class WebScrape:
    def __init__(self):
        self.web_address = 'https://.......'

    def check_word_exists(self, word):
        page = requests.get(self.web_address + word)
        sleep(random.randint(7, 10))
        soup = BeautifulSoup(page.text, 'html.parser')
        suggestions_text = soup.find_all('div', {'id': 'MainTxt'})
        heading = soup.find_all('h1')
        try:
            if "Word not found" in suggestions_text[0].text.strip() or 'is not available in the general English' in suggestions_text[0].text.strip() or 'Variant of' in suggestions_text[0].text.strip():
                return False
            elif len(suggestions_text) == 0:
                return False
            else:
                if heading[0].text == word.lower():
                    return True
                else:
                    return False
        except Exception:
            return False

    def check_presence_of_number(self, word):

        return any(i.isdigit() for i in word)

    def get_phrases(self, word):
        phrases_list = []
        phrases_collection = []
        page = requests.get(self.web_address + word)
        sleep(random.randint(7, 10))
        try:
            soup = BeautifulSoup(page.text, 'html.parser')
            phrase_def = soup.find_all('div', {'id': 'ThesaurusInner'})

            first_section = phrase_def[0].find_all('section', {'data-src': 'wn'})
            if len(first_section) != 0:
                first_count = first_section[0].find_all('tr', {'': ''})
                figure_speech = first_count[0].find_all('td', {'style': 'vertical-align:top'})

                for i in range (len(first_count)):
                    fig_of_speech = first_count[i].find_all('td', {'style': 'vertical-align:top'})
                    if (fig_of_speech[0].text.strip()) != '':
                        figure_speech = fig_of_speech[0].text
                    all_synonyms = first_count[i].find_all('div', {'class': 'Syn'})
                    for j in range(len(all_synonyms)):
                        synonyms_phrase = (all_synonyms[j].text).split(',')
                        for synonym in synonyms_phrase:
                            phrases_list.append(synonym.strip().strip('.') + '|' + word + '|' + figure_speech.lower())

                    phrases = first_count[i].find_all('div', {'class': 'Rel'})
                    for k in range (len(phrases)):
                        total_word_phrase = phrases[k].text.split('-')
                        word_phrase = (total_word_phrase[0].strip()).split(',')
                        for expression in word_phrase:
                            phrases_list.append(expression.strip().strip('.') + '|' + word + '|' + figure_speech.lower())

            second_section = phrase_def[0].find_all('section', {'data-src': 'hc_thes'})
            if len(second_section) != 0:
                second_count = second_section[0].find_all('div', {'': ''})
                for count in second_count:
                    figure_of_speech = ''
                    for i in range(len(count.text)):
                        if str(count.text[i]).isdigit():
                            break
                        else:
                            figure_of_speech = figure_of_speech + str(count.text[i])
                    if figure_of_speech != '':
                        figure_speech = figure_of_speech
                    all_phrases = count.find_all('div', {'class': 'ds-list'})
                    for l in range(len(all_phrases)):
                        phrases = all_phrases[l].find_all('span', {'class': 'Syn'})
                        for j in range(len(phrases)):
                            expression = phrases[j].text.split(',')
                            for k in range(0, len(expression)):
                                if 'LUV' in expression[k]:
                                    break
                                expression[k] = re.sub(r'[0-9]+\.', '', expression[k])
                                phrases_list.append(expression[k].strip().strip('.') + '|' + word + '|' + figure_speech.lower())

            third_section = phrase_def[0].find_all('section', {'data-src': 'hm_thes'})
            list_of_speech = []
            speech = []
            if len(third_section) != 0:
                all_phrases = third_section[0].find_all('div', {'class': 'pseg'})
                all_fig_of_speech = third_section[0].find_all('i')

                for fig_of_speech in all_fig_of_speech:
                    list_of_speech.append(fig_of_speech.text)
                for j in range(len(list_of_speech)):
                    list_of_speech[j] = str.replace(list_of_speech[j], 'phrasal verb', 'verb')
                    if list_of_speech[j] in ['verb', 'noun', 'adverb', 'adjective']:
                        speech.append(list_of_speech[j])
                for i in range(len(all_phrases)):
                    all_synonyms = all_phrases[i].find_all('div', {'class': 'Syn ds-list'})
                    for synonyms in all_synonyms:
                        expression = synonyms.text.split(',')
                        for phrase in expression:
                            phrase = re.sub(r'[a-zA-Z]+\:', '', phrase)
                            phrases_list.append(phrase.strip('.').strip().strip('.') + '|' + word + '|' + speech[i].lower())
        except Exception:
            return None
        for i in range(len(phrases_list)):
            if len(phrases_list[i].split()) > 1:
                phrases_collection.append(phrases_list[i].strip())

        return phrases_collection

    def write_into_file(self, word, filename):
        phrases_collection = self.get_phrases(word)
        if phrases_collection != None:
            with open(filename, 'a') as f:
                for i in range (0, len(phrases_collection)):
                    f.write(phrases_collection[i] + '\n')
            f.close()


    def read_words_from_file(self, file_path, output_file, flag_word=None):
        file = open(file_path, 'r')
        reader = csv.reader(file)
        is_readable = False
        for word in reader:
            if flag_word is None:
                is_readable = True
            elif not is_readable:
                if word[0] == flag_word.strip():
                    is_readable = True

            if is_readable and  len(str(word[0].strip()))>1:
                if not self.check_presence_of_number(str(word[0].strip())):
                    print('processing: ' + word[0])
                    if self.check_word_exists(str(word[0]).strip()):
                        self.write_into_file(str(word[0]).strip(), output_file)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--word_list', default = '/......./words.txt')
    parser.add_argument('--phrase_extraction', default = 'output.txt')
    parser.add_argument('--word')
    args = parser.parse_args()
    WebScrape().read_words_from_file(args.word_list, args.phrase_extraction, args.word)
