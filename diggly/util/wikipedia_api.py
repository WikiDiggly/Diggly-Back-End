import sys
reload(sys);
sys.setdefaultencoding("utf8")

import os
import requests
import random

from text_process import Text_Process
from .diggly_serializers import TopicManager, TopicLinkManager, TopicLinkSerializer
from ..models import Topic, TopicLink

# 2016 wikidiggly
# author: ola-halima
# prototype v1

rev_url= "https://en.wikipedia.org/w/api.php?&format=json&formatversion=2&action=query&prop=revisions&rvprop=content&{}"
extract_url= "https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&explaintext=&{}"
parse_url= "https://en.wikipedia.org/w/api.php?action=parse&prop=sections|links&contentformat=text/plain&pageid={}"
linked_topics_url = "https://en.wikipedia.org/w/api.php?format=json&action=query&prop=links&pllimit=3&plnamespace=0&{}"
sections_url = "https://en.wikipedia.org/w/api.php?action=parse&prop=sections&pageid=25202"
wiki_url_base= "https://en.wikipedia.org/wiki/{}"

rvcont= "&rvcontinue={}"
excont= "&excontinue={}"
plcont= "&plcontinue={}"

exintro= "&exintro="
exsentences= "&exsentences={}"
r_title= "titles={}"
r_pageid= "pageids={}"
arg_sep= "|" 
title_sep = "_"

class WikipediaHelper():
    #desc_length = 6
    #summ_length = 1 
    #t_processor = None
    #t_creator = None
    #tl_creator = None

    @classmethod
    def __init__(self, desc_len, summ_len): 
        self.desc_length = desc_len
        self.summ_length = summ_len    
    
        self.t_processor = Text_Process(self.desc_length, self.summ_length)
        self.t_creator = TopicManager()
        self.tl_creator = TopicLinkManager()

    def get_article(self, r_args):
        nlinks = self.__count_articles(r_args)
        resources = self.__format_req(r_args)
        r_url = extract_url.format(resources)
        retrieve_flag = "extract"
        #for tests
        #nlinks = 2|3 
        #r_url = extract_url.format(r_title.format("Absolute_zero|Pluto|August_14"))
        #r_url = extract_url.format(r_pageid.format("1418|1417"))
        
        pages = self.make_query_request(r_url, excont, retrieve_flag, nlinks)
        topics = self.__parse_pages(pages)

        for tp in topics:
            self.add_linked_topics(tp) #retrieve linked topics

        return topics

    def add_linked_topics(self, source_topic): 
        tid = source_topic.article_id
        source_page = r_pageid.format(tid)
        nlinks = 1 #number of articles
        r_url = linked_topics_url.format(source_page)

        #TODO: check if plcontinue flag is True
        retrieve_flag = "links"
        pages = self.make_query_request(r_url, None, retrieve_flag, nlinks) #TODO: add plcontinue support
        linked_titles = self. __parse_linked_pages(tid, pages)    

        #create topic objects for linked topics
        r_url = extract_url.format(r_title.format(arg_sep.join(linked_titles))) 
        nlinks =  self.__count_articles(linked_titles)
        retrieve_flag = "extract"
        linked_pages = self.make_query_request(r_url, excont, retrieve_flag,  nlinks)
        linked_topics = self.__parse_pages(linked_pages)
        topiclinks = []

        #create topiclink relation for linked_topics
        for topic in linked_topics:
            reltext = topic.article_title + " is linked to " + source_topic.article_title
            tldata = {"source_id" : source_topic,
                    "target_id" : topic,
                    "title" : topic.article_title,
                    "description" : reltext,
                    "wiki_link" : topic.wiki_link,
                    "score" : self.__get_link_score(source_topic, topic)
                    }

            tlink = self.tl_creator.create_topiclink(tldata)
            #tlink.save()
            topiclinks.append(tlink)

        sorted_tl = sorted(topiclinks, key=lambda instance: instance.score, reverse=True)
        num_links = 2
        
        #to prevent Index out of bounds error on sorted_tl
        i = 0
        for tl in sorted_tl:
            if (i <= num_links):
                source_topic.linked_topics.append(tl)        
                i = i + 1
            else:
                break

        #source_topic.save()
        #return source_topic        

    #private functions
    def __get_link_score(self, source, target):
        #TODO: implement algorithm for topic relatedness  
        i = 0
        stop = random.randrange(20, 99)
        for i in range(stop):
            i /= 100.0
        
        return i #randomly generated score 

    def __parse_linked_pages(self, source_id, pages):
        if pages != None:
            titles = []
            print "\n\n\nPAGES (links)", pages, "\n\n"
            links = pages[str(source_id)]["links"]

            if links != None:
                for lk in links:
                   titles.append(lk["title"].replace(" ", title_sep)) #get title of linked article

            return titles
    
    def __parse_pages(self, pages):
        topics = []

        for pid in pages:
            #TODO: trim content length from api call
            topic = None
            
            try:
                topic = Topic.objects.get(article_id=pid)
            
            except Topic.DoesNotExist:
                pcontent = pages[pid]
                title = pcontent['title']
                #print "\n\nPCONTENT ---> ", pcontent, "\n\n"
            
                content = pcontent['extract'].encode('utf-8') #TODO: fix this to make bug proof
                parsedtext = self.t_processor.get_desc_summ(content)

                data = {"article_id" : int(pid),
                        "article_title" : title,
                        "description" : parsedtext[self.t_processor.desc_text],
                        "summary" : parsedtext[self.t_processor.summ_text],
                        "wiki_link" : wiki_url_base.format(title.replace(" ", title_sep)),
                        "linked_topics" : []
                        }
                #TODO: fix url generation

                topic = self.t_creator.create_topic(data)     
                topic.save() 
         
            if topic != None:   
                topics.append(topic)
        
        return topics

    #def __get_article_links(self, r_args):
    #    nlinks = self.__count_articles(r_args)
    #    resources = self.__format_req(r_args)
    #    r_url = extract_url.format(resources)

    #    pages = self.make_query_request(r_url, "excontinue", nlinks)
    #    topics = self.__parse_pages(pages)
 
    #    return topics

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

    def request_pages_plain(self, url):
        print "\nURL --->\n", url   
        resp = requests.get(url)
        
        if resp.status_code != 200:
            #TODO: handle exception better
            raise ApiError('GET: api request error\n{}'.format(resp.status_code))
            return None 

        #TODO: catch Exception for "No JSON object could be decoded"
        json_response = resp.json()
        pages = json_response['query']['pages']        
    
        return pages
    
    def make_query_request(self, r_url, cont_flag, retrieve_flag, nlinks):
        #TODO: continue flag if neccessary
        all_pages = {}
        index = 0;
        c_flag = "continue"
        is_continue = True

        while (nlinks > 0 and is_continue == True):
            url = r_url
            
            if cont_flag != None:
                url = url + cont_flag.format(index)
        
            print "\nRURL --->\n", r_url
            print "\nURL --->\n", url   
            resp = requests.get(url)
            if resp.status_code != 200:
                #TODO: handle exception better
                raise ApiError('GET: api request error\n{}'.format(resp.status_code))
                return None 

            #TODO: catch Exception for "No JSON object could be decoded"
            json_response = resp.json()
            pages = json_response['query']['pages']
            #print "\n\n\nMAKE_REQUEST_PAGES--->", pages, "\n\n"              
 
            curr_pid = -1
            for key,val in pages.iteritems():
                #print "KEY-->", key, "VAL--->", val
                #print "\nRETRIEVE_FLAG -->", retrieve_flag
                if retrieve_flag in val:
                    curr_pid = key
                    break #TODO: break here or continue running

            #print "\n CUR_PID -->", curr_pid, "\n"
            #print "INDEX -->", index, "\n"
            #print "\nPAGES[PID] -->", pages[curr_pid], "\n\n"
            
            #should always be true
            if curr_pid > -1:
                all_pages.update({curr_pid : pages[curr_pid]})        

            if c_flag in json_response:
                index = index + 1
            else:
                is_continue = False 
            
            nlinks = nlinks - 1
       
        print "\n\n\nALL_PAGES", all_pages, "\n\n" 
        return all_pages

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
