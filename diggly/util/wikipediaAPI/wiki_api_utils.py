import random
import sys

import re
import requests
from diggly.models import Topic
from diggly.util.serializers.topic_serializers import TopicManager, TopicLinkManager, TopicRedirectManager
from diggly.util.text_processor.text_process import Text_Process
from diggly.util.wikipediaAPI.wiki_constants import *

reload(sys);
sys.setdefaultencoding("utf8")

# 2016 wikidiggly

class WikiAPIUtils():
    @classmethod
    def __init__(self, desc_len, summ_len):
        self.desc_length = desc_len
        self.summ_length = summ_len

        self.t_processor = Text_Process()
        self.t_creator = TopicManager()
        self.tl_creator = TopicLinkManager()
        self.rd_creator = TopicRedirectManager()

    # util functions
    def get_rand_score(self, source, target):
        #TODO: implement algorithm for topic relatedness
        i = 0
        stop = random.randrange(20, 99)
        for i in range(stop):
            i /= 100.0

        return i # randomly generated score

    def fetch_relevant_topics(self, title_list, num_res):
        res = []

        while (len(res) < num_res):
            max_index = len(title_list)
            index = random.randrange(0, max_index)
            title = title_list[index]

            if not title in res:
                res.append(title)
                title_list.remove(title)

        title_list.extend(res)
        return res

    def parse_linked_pages(self, source_id, pages):
        if pages != None:
            pattern = re.compile(r'\d\$,')
            titles = []
            links = pages[str(source_id)]["links"]

            if links != None:
                for lk in links:
                    lk_title = lk["title"]
                    # if re.match(r'^\w+$', lk_title):
                    if re.match(r'^[a-zA-Z-_() ]+$', lk_title):
                        clean_title = self.clean_topic_title(lk_title)
                        titles.append(clean_title) # get title of linked article

            return titles

    def parse_and_save_topic(self, pages, redirects):
        topics = []

        for pid in pages:
            # TODO: trim content length from api call
            topic = None

            try:
                topic = Topic.objects.get(article_id=pid)

            except Topic.DoesNotExist:
                pcontent = pages[pid]
                title = pcontent['title']

                content = pcontent['extract'].encode('utf-8') # TODO: fix this to make bug proof
                parsedtext = self.t_processor.get_desc_summ(content)

                data = {"article_id" : int(pid),
                        "article_title" : title,
                        "description" : parsedtext[self.t_processor.desc_text],
                        "summary" : parsedtext[self.t_processor.summ_text],
                        "wiki_link" : WIKI_URL_BASE.format(self.clean_topic_title(title)),
                        "linked_topics" : []
                        }

                topic = self.t_creator.create_topic(data)

                # continue if there are no page redirects
                if redirects != None or bool(redirects) != False:
                    # print "\n\nREDIRECTS -->", redirects
                    for rd in redirects:
                        rdfrom = rd['from']
                        rdto = rd['to']

                        if title == rdto:
                            topic_rd = self.create_topic_redirect(rdfrom, topic)
                            topic_rd.save()
                            redirects.remove(rd)

                topic.save()

            if topic != None:
                topics.append(topic)

        return topics

    def create_topic_redirect(self, source_rd_title, target_rd_topic):
        source_rd_id = self.convert_titles_to_ids([source_rd_title])[0]

        data = {"source_id" : source_rd_id, "redirect_topic" : target_rd_topic}
        topic_rd = self.rd_creator.create_topic_redirect(data)
        return topic_rd

    def request_api_pages_plain(self, url):
        print "\nREQUEST URL --->\n", url
        resp = requests.get(url)

        if resp.status_code != 200:
            # TODO: handle exception better
            raise requests.HTTPError('GET: Wikipedia api request error\n{}'.format(resp.status_code))
            return None

        # TODO: catch Exception for "No JSON object could be decoded"
        json_response = resp.json()
        pages = json_response['query']['pages']

        return pages

    def make_api_request(self, r_url, cont_flag, retrieve_flag):
        all_pages = {}

        c_flag = "continue"
        ct_flag = self.format_flag(cont_flag)
        next_flag = ""

        is_first = True
        is_continue = False
        redirects = None

        while (is_continue == True or is_first == True):
            url = r_url

            if is_continue == True:
                url = url + ct_flag.format(next_flag)

            print "\nREQUEST URL --->\n", url
            resp = requests.get(url)
            if resp.status_code != 200:
                # TODO: handle exception better
                raise requests.HTTPError('GET: api request error\n{}'.format(resp.status_code))
                return None

            # TODO: catch Exception for "No JSON object could be decoded"
            json_response = resp.json()
            query = json_response['query']
            pages = query['pages']

            if 'redirects' in query:
                redirects = query['redirects']

            curr_pid = -1
            for key,val in pages.iteritems():
                if retrieve_flag in val:
                    curr_pid = key
                    break # TODO: break here or continue running?

            # should always be true
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

        results = {PAGE_RESP_KEY : all_pages}

        if redirects != None:
            results.update({REDIRECT_RESP_KEY : redirects})

        return results

    def convert_titles_to_ids(self, titles):
        resources = self.format_req(titles)
        url = PAGE_INFO_URL.format(resources)
        pages = self.request_api_pages_plain(url)

        if pages == None:
            # TODO: error handling
            return []

        ids = []
        for pgval in pages.values():
            tid = pgval['pageid']
            ids.append(tid)

        return ids

    def convert_ids_to_titles(self, ids):
        resources = self.format_req(ids)
        url = PAGE_INFO_URL.format(resources)
        pages = self.request_pages_plain(url)

        if pages == None:
            # TODO: error handling
            return []

        titles = []
        for pgval in pages.values():
            clean_title = self.clean_topic_title(pgval['title'])
            titles.append(clean_title)

        return titles

    def clean_topic_title(self, title):
        # capitalize = re.sub(r'\w+', lambda m:m.group(0).capitalize(), title)
        clean_title = title.replace(" ", TITLE_SEP)
        return clean_title

    def is_pageid(self, arg):
        try:
            pid = int(arg)
            return True;

        except ValueError:
            return False;

    def is_seq(self, arg):
        return (not hasattr(arg, "strip") and
                hasattr(arg, "__getitem__") or
                hasattr(arg, "__iter__"))

    def count_articles(self, r_args):
        if self.is_seq(r_args):
            return len(r_args)

        # default
        return 1

    def format_req(self, r_args):
        if self.is_seq(r_args): # check if arg is a list
            if self.is_pageid(r_args[0]):
                return R_PAGEID.format(ARG_SEP.join(r_args))
            else:
                return R_TITLE.format(ARG_SEP.join(r_args))

        if self.is_pageid(r_args):
            return R_PAGEID.format(r_args)

        # default return single page title format
        return R_TITLE.format(r_args)

    def format_flag(self, flag):
        newflag = "&{}="
        return newflag.format(flag) + "{}"
