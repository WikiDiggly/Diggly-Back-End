import nltk
import sys;
reload(sys);
sys.setdefaultencoding("utf8")


# 2016 wiki_diggly
# author: ola-halima
# prototype v1
# This class is a diggly wrapper for the nltk text processing library functionalities

class Text_Process():
    desc_text = "description"    
    summ_text = "summary"    

    @classmethod
    def __init__(self, desc_len, summ_len): 
        self.desc_length = desc_len
        self.summ_length = summ_len 

    def get_description(self, content):
        desc = self.__get_sentences(content, self.desc_length) 
        return desc

    def get_summary(self, content):
        summ = self.__get_sentences(content, self.summ_length)
        return summ

    #preferred to use this function
    def get_desc_summ(self, content):
        desc = self.get_description(content)
        summ = self.get_summary(desc)

        res = {self.desc_text : desc, self.summ_text : summ}
        return res   

    #private functions
    def __get_sentences(self, content, length):
        #print "CONTENT in TEXT_PROCESS -->", content
        sentences = nltk.sent_tokenize(content.decode('utf-8'))
        res = " ".join(sentences[0:length]) 
        return res

    def __get_words(self, content, length):
        #TODO: implement 
        res = ""
        return res
     
