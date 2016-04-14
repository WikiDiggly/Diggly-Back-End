import nltk
import string
import sys

from collections import Counter
from nltk.corpus import stopwords
from nltk.stem.porter import *

from diggly.util.wikipediaAPI.wiki_constants import *

reload(sys)
sys.setdefaultencoding("utf8")


# 2016 wiki_diggly
# This class is a diggly wrapper for the nltk text processing library functionalities
# ref: http://www.cs.duke.edu/courses/spring14/compsci290/assignments/lab02.html

class Text_Process():
    desc_text = "description"    
    summ_text = "summary"
    stemmer = PorterStemmer()

    @classmethod
    def __init__(self):
        self.desc_length = DEFAULT_DESC_LENGTH
        self.summ_length = DEFAULT_SUMM_LENGTH

    def get_description(self, content):
        desc = self.__get_sentences(content, self.desc_length) 
        return desc

    def get_summary(self, content):
        summ = self.__get_sentences(content, self.summ_length)
        return summ

    # preferred to use this function
    def get_desc_summ(self, content):
        desc = self.get_description(content)
        summ = self.get_summary(desc)

        res = {self.desc_text : desc, self.summ_text : summ}
        return res

    def tokenize(self, text):
        tokens = self.get_tokens(text)
        stems = self.stem_tokens(tokens)
        return stems


    def clean_text(self, text):
        tokens = self.get_tokens(text)
        filtered = [w for w in tokens if not w in stopwords.words('english')]

        filter_count = Counter(filtered)
        print filter_count.most_common(100)

        stemmed = self.stem_tokens(filtered)

        stem_count = Counter(stemmed)
        print stem_count.most_common(100)
        return

    def get_tokens(self, text):
        lowers = text.lower()

        # remove the punctuation using the character deletion step of translate
        remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)
        no_punctuation = lowers.translate(remove_punctuation_map)
        tokens = nltk.word_tokenize(no_punctuation)
        return tokens

    def stem_tokens(self, tokens):
        stemmed = []
        for item in tokens:
            stemmed.append(self.stemmer.stem(item))
        return stemmed

    # private functions
    def __get_sentences(self, content, length):
        sentences = nltk.sent_tokenize(content.decode('utf-8'))
        res = " ".join(sentences[0:length])
        return res

    def __get_words(self, content, length):
        #TODO: implement 
        res = ""
        return res
     
