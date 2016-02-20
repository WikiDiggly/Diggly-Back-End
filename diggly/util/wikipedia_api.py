import sys
reload(sys);
sys.setdefaultencoding("utf8")

import os
import re
import requests
import random

from text_process import Text_Process
from .diggly_serializers import TopicManager, TopicLinkManager, TopicLinkSerializer
from ..models import Topic, TopicLink

# 2016 wikidiggly
# prototype v1

page_info_url= "https://en.wikipedia.org/w/api.php?format=json&action=query&{}"
extract_url= "https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&explaintext=&{}"
parse_url= "https://en.wikipedia.org/w/api.php?action=parse&prop=sections|links&contentformat=text/plain&pageid={}"
linked_topics_url = "https://en.wikipedia.org/w/api.php?format=json&action=query&prop=links&pllimit=max&plnamespace=0&{}"
sections_url = "https://en.wikipedia.org/w/api.php?action=parse&prop=sections"
redirect_url = "https://en.wikipedia.org/w/api.php?format=json&action=query&prop=langlinks&redirects=&{}"
wiki_url_base= "https://en.wikipedia.org/wiki/{}"

rvcont= "rvcontinue"
excont= "excontinue"
plcont= "plcontinue"

exintro= "&exintro="
exsentences= "&exsentences={}"
r_title= "titles={}"
r_pageid= "pageids={}"
arg_sep= "|" 
title_sep = "_"

class WikipediaHelper():

    @classmethod
    def __init__(self, desc_len, summ_len): 
        self.desc_length = desc_len
        self.summ_length = summ_len    
    
        self.t_processor = Text_Process(self.desc_length, self.summ_length)
        self.t_creator = TopicManager()
        self.tl_creator = TopicLinkManager()

    def get_article(self, r_args):
        if self.__is_seq(r_args) == False:
            r_args = [r_args]
            print "\n\n CONVERTING R_ARGS to list -->", r_args

        redirect_ids = self.__get_page_redirect(r_args)
        resources = self.__format_req(redirect_ids)
        r_url = extract_url.format(resources)

        retrieve_flag = "extract"  
        pages = self.make_query_request(r_url, excont, retrieve_flag)
        topics = self.__parse_and_save_topic(pages)

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
        pages = self.make_query_request(r_url, plcont, retrieve_flag) #TODO: add plcontinue support
        linked_titles = self. __parse_linked_pages(tid, pages)    

        print "\n\nLINKED_TITLES -->", linked_titles
        print "\nlen(LINKED_TITLES) -->", len(linked_titles)

        #select 3 random topics
        rel_links = self.__fetch_relevant_topics(linked_titles, 3)
        source_topic.outlinks = linked_titles

        print "\n\nNEW LINKED_TITLES -->", linked_titles
        print "\nNEW len(LINKED_TITLES) -->", len(linked_titles)

        #for testing
        #return

        #create topic objects for linked topics
        r_url = extract_url.format(r_title.format(arg_sep.join(rel_links)))
        retrieve_flag = "extract"
        linked_pages = self.make_query_request(r_url, excont, retrieve_flag)
        linked_topics = self.__parse_and_save_topic(linked_pages)
        topiclinks = []

        #create topiclink relation for linked_topics
        for topic in linked_topics:
            reltext = topic.article_title + " is linked to " + source_topic.article_title
            tldata = {"source_id" : source_topic,
                    "target_id" : topic,
                    "title" : topic.article_title,
                    "description" : reltext,
                    "wiki_link" : topic.wiki_link,
                    "score" : self.__get_rand_score(source_topic, topic)
                    }

            tlink = self.tl_creator.create_topiclink(tldata)
            topiclinks.append(tlink)

        sorted_tl = sorted(topiclinks, key=lambda instance: instance.score, reverse=True)
        num_links = 2
        
        #to prevent Index out of bounds error on sorted_tl
        i = 0
        for tl in sorted_tl:
            if (i <= num_links):
                source_topic.linked_topics.append(tl)        
                i = i + 1

        source_topic.save()

    #private functions
    def __fetch_relevant_topics(self, title_list, numRes):
        res = []
        maxIndex = len(title_list)

        while (len(res) < numRes):
            index = random.randrange(0, maxIndex)
            title = title_list[index]

            if not title in res:
                res.append(title)
                title_list.remove(title)
        
        redirect_ids = self.__get_page_redirect(res)
        redirect_titles = self.__convert_ids_to_titles(redirect_ids)

        title_list.extend(redirect_titles)
        return redirect_titles    

    def __get_rand_score(self, source, target):
        #TODO: implement algorithm for topic relatedness  
        i = 0
        stop = random.randrange(20, 99)
        for i in range(stop):
            i /= 100.0
        
        return i #randomly generated score 

    def __parse_linked_pages(self, source_id, pages):
        if pages != None:
            pattern = re.compile(r'\d\$,')
            titles = []
            #print "\n\n\nPAGES (links)", pages, "\n\n"
            links = pages[str(source_id)]["links"]

            if links != None:
                for lk in links:
                    lk_title = lk["title"]
                    #if re.match(r'^\w+$', lk_title):          
                    if re.match(r'^[a-zA-Z-_() ]+$', lk_title): 
                        clean_title = self.__clean_topic_title(lk_title)    
                        titles.append(clean_title) #get title of linked article

            return titles
    
    def __parse_and_save_topic(self, pages):
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
                        "wiki_link" : wiki_url_base.format(self.__clean_topic_title(title)),
                        "linked_topics" : []
                        }

                topic = self.t_creator.create_topic(data)     
                topic.save() 
         
            if topic != None:   
                topics.append(topic)
        
        return topics

    def __get_page_redirect(self, r_args):
        resources = self.__format_req(r_args)
        url = redirect_url.format(resources)
        resp = requests.get(url)

        if resp.status_code != 200:
            raise ApiError('GET: api request error\n{}'.format(resp.status_code))
            return None

        json_response = resp.json()
        query = json_response['query']

        if 'redirects' not in query:
            return r_args

        redirects = query['redirects']
        pages = json_response['query']['pages']
        redirect_ids = pages.keys()

        print "\n\nREDIRECTS -->", redirects
        print "\nR_ARGS -->", r_args
        print "\nREDIRECT IDS -->", redirect_ids

        return redirect_ids


    def request_pages_plain(self, url):
        print "\nURL --->\n", url   
        resp = requests.get(url)
      
        if resp.status_code != 200:
            #TODO: handle exception better
            raise ApiError('GET: Wikipedia api request error\n{}'.format(resp.status_code))
            return None 

        #TODO: catch Exception for "No JSON object could be decoded"
        json_response = resp.json()
        pages = json_response['query']['pages']        
    
        return pages
    
    def make_query_request(self, r_url, cont_flag, retrieve_flag):
        all_pages = {}
        
        c_flag = "continue"
        ct_flag = self.__format_flag(cont_flag)
        next_flag = ""

        is_first = True
        is_continue = False

        while (is_continue == True or is_first == True):
            url = r_url
            
            if is_continue == True:
                url = url + ct_flag.format(next_flag)
        
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
 
            curr_pid = -1
            for key,val in pages.iteritems():
                if retrieve_flag in val:
                    curr_pid = key
                    break #TODO: break here or continue running

            #print "\n CUR_PID -->", curr_pid, "\n"
            #print "INDEX -->", index, "\n"
            #print "\nPAGES[PID] -->", pages[curr_pid], "\n\n"
            
            #should always be true
            if curr_pid > -1:
                if curr_pid in all_pages:
                    all_pages[curr_pid][retrieve_flag].extend(pages[curr_pid][retrieve_flag])
                else:    
                    all_pages.update({curr_pid : pages[curr_pid]})        

            if c_flag in json_response:
                is_continue = True
                next_flag = json_response[c_flag][cont_flag]
            else:
                is_continue = False 
            
            is_first = False
       
        return all_pages

    def __convert_ids_to_titles(self, ids):
        resources = self.__format_req(ids)
        url = page_info_url.format(resources)
        pages = self.request_pages_plain(url)

        if pages == None:
            #TODO: error handling
            return []

        titles = []
        for pgval in pages.values():
            clean_title = self.__clean_topic_title(pgval['title'])
            titles.append(clean_title)

        return titles

    def __clean_topic_title(self, title):
        #capitalize = re.sub(r'\w+', lambda m:m.group(0).capitalize(), title)
        clean_title = title.replace(" ", title_sep) 
        return clean_title

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

    def __format_flag(self, flag):
        newflag = "&{}="
        return newflag.format(flag) + "{}"
