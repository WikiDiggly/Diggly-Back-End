import os
import requests
from diggly.util.serializers.topic_serializers import TopicManager, TopicLinkManager
from diggly.util.text_processor.text_process import Text_Process
from diggly.util.wikipediaAPI.wiki_api import WikipediaHelper

pageid_convert_url="https://en.wikipedia.org/w/api.php?action=query&format=json&{}"
jpedia_base_url="https://michelemostarda-JSONpedia-v1.p.mashape.com/annotate/resource/json/{}?&procs=extractors"

eng_entity= "en:{}"
r_title= "titles={}"
r_pageid= "pageids={}"
arg_sep= "|"
title_sep = "_"

class JsonPediaManager():
    #desc_len = 6
    #summ_len = 1
    #t_processor = Text_Process(desc_len, summ_len)
    #t_mgt = TopicManager()
    #tl_mgt = TopicLinkManager()
    #wk_mgt = WikipediaHelper(description_len, summary_len)

    @classmethod
    def __init__(self, desc_len, summ_len):
        self.desc_length = desc_len
        self.summ_length = summ_len

        self.t_processor = Text_Process(self.desc_length, self.summ_length)
        self.wk_mgt = WikipediaHelper(self.desc_length, self.summ_length)
        self.t_creator = TopicManager()
        self.tl_creator = TopicLinkManager()

    def get_article(self, r_args):
        nlinks = self.__count_articles(r_args)
        titles = self.__get_article_titles(r_args, nlinks)

        print "TITLES -->", titles 
        for a_title in titles:
            r_entity = eng_entity.format(a_title)
            r_url = jpedia_base_url.format(r_entity) 

            self.__fetch_article(r_url)   

    def __fetch_article(self, url):
        print "\nURL --->\n", url  
        headers={
            "X-Mashape-Key": os.environ['MASHAPE_KEY'],
            "Accept": "application/json"
        } 

        resp = requests.get(url, headers=headers)
        print "RESP STATUS CODE -->", resp.status_code
        print "RESP -->", resp.text

        if resp.status_code != 200:
            #TODO: handle exception better
            raise requests.ApiError('GET: Jsonpedia api request error\n{}'.format(resp.status_code))
            return None 
    
        json_response = resp.json()
        pid = json_response['revid'] 

        print "JSONPEDIA PID -->", pid

    def __get_article_titles(self, r_args, nlinks):
        resources = self.__format_req(r_args) #assume you receive pageids
        #resources = "pageids=26903|26521"
        r_url = pageid_convert_url.format(resources)

        retrieveflag = "title"
        titles = []
        pages = self.wk_mgt.request_pages_plain(r_url, False) 
       
        #print "PAGES IN JSONPE -->", pages 
        for pid,page in pages.iteritems():
            a_title = page[retrieveflag].strip()
            titles.append(a_title.replace(" ", title_sep))
        
        #return arg_sep.join(titles)
        return titles

    def __count_articles(self, r_args):
        if self.__is_seq(r_args):
            return len(r_args)

        #default
        return 1

    def __format_req(self, r_args):
        if self.__is_seq(r_args): # check if arg is a list
            if self.__is_pageid(r_args[0]):
                return r_pageid.format(arg_sep.join(r_args))
            else:
                return r_title.format(arg_sep.join(r_args))

        if self.__is_pageid(r_args):
            return r_pageid.format(r_args)

        #default return single page title format
        return r_title.format(r_args)
    
    def __is_pageid(self, arg):
        try:
            pid = int(arg)
            return True;

        except ValueError:
            return False;   

    def __is_seq(self, arg):
        return (not hasattr(arg, "strip") and
                hasattr(arg, "__getitem__") or
                hasattr(arg, "__iter__"))
