import nltk

# 2016 wiki_diggly
# author: ola-halima
# prototype v1
# This class is a diggly wrapper for the nltk text processing library functionalities

class Text_Process():
    @classmethod
    def __init__(self, desc_len, sum_len): 
        self.desc_length = desc_len
        self.sum_length = sum_len 

    def get_description(self, content):
        desc = __get_sentences(content, desc_length) 

        return desc

    def get_summary(self, content):
        summ = ""

        return summ

    #preferred to use this function
    def get_desc_summ(self, content):
        desc = get_description(content)
        summ = get_summary(desc)

        res = {}

        return res   

    #private functions
    def __get_sentences(self, content, length):
        sentences = nltk.sent_tokenize(content)
        res = sentences[0 : length] 

        return res

    def __get_words(self, content, length):
        res = ""

        return res
     
        

