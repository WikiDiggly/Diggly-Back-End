import random
import threading

from diggly.util.text_processor.score_process import score_topics
from diggly.util.serializers.topic_serializers import TopicLinkManager
from diggly.util.wikipediaAPI.wiki_api_utils import WikiAPIUtils
from diggly.util.wikipediaAPI.wiki_constants import *

# 2016 wikidiggly

thread_lock1 = threading.Lock()
thread_lock2 = threading.Lock()
thread_lock3 = threading.Lock()


class WikipediaHelper():
    desc_length = DEFAULT_DESC_LENGTH
    summ_length = DEFAULT_SUMM_LENGTH

    @classmethod
    def __init__(self):
        self.tl_creator = TopicLinkManager()
        self.api_utils = WikiAPIUtils(self.desc_length, self.summ_length)

    def get_article(self, r_args):
        if self.api_utils.is_seq(r_args) == False:
            r_args = [r_args]

        resources = self.api_utils.format_req(r_args)
        r_url = EXTRACT_URL.format(resources)

        retrieve_flag = "extract"
        response = self.api_utils.make_api_request(r_url, EXCONT, retrieve_flag)
        pages = response[PAGE_RESP_KEY]
        redirects = response[REDIRECT_RESP_KEY] if REDIRECT_RESP_KEY in response else None

        topics = self.api_utils.parse_and_save_topic(pages, redirects)

        for tp in topics:
            self.add_linked_topics(tp)  # retrieve linked topics

        return topics

    def add_linked_topics(self, source_topic):
        tid = source_topic.article_id
        num_linked_topics = DEFAULT_NUM_LINKED_TOPICS - len(source_topic.linked_topics)
        max_linked_topics = MAX_NUM_LINKED_TOPICS - len(source_topic.linked_topics)
        source_page = R_PAGEID.format(tid)
        r_url = LINKED_TOPICS_URL.format(source_page)

        retrieve_flag = "links"
        response = self.api_utils.make_api_request(r_url, PLCONT, retrieve_flag)
        pages = response[PAGE_RESP_KEY]
        linked_titles = self.api_utils.parse_linked_pages(tid, pages)

        # select 6 random topics
        # rel_links = self.fetch_relevant_topics(linked_titles, num_linked_topics)
        rel_links = self.fetch_relevant_topics(linked_titles, max_linked_topics)
        source_topic.outlinks = linked_titles
        all_linked_topics = []

        # for testing
        # return

        try:
            thread_count = 1
            topic_desc_dict = {}
            threads = []
            rel_topics = []

            topic_desc_dict.update({source_topic.article_id: source_topic.description})

            #spun threads to create topic objects
            for i in range(1, MAX_NUM_THREADS + 1):
                tmp_thread = FuncThread(thread_count, self.spun_topic_creator, rel_links,
                                        rel_topics, topic_desc_dict)
                tmp_thread.start()
                threads.append(tmp_thread)
                print "Spun Topic Creator Thread #", thread_count, "\n"
                thread_count += 1

            # wait for threads to return
            for t in threads:
                t.join()

            print "Continuing Main Thread after topic creation...\n"

            # calculate score of related topics
            print "About to start calculating scores\n"
            scored_desc_dict = score_topics(source_topic.article_id, topic_desc_dict)

            for a, b in scored_desc_dict.iteritems():
                print a, "-->", b, "\n"
            print "\n Done Computing NEW SCORES FOR TOPICS:\n"

            # spun threads to create topic links
            del threads[:]
            topic_links = []
            for i in range(1, MAX_NUM_THREADS + 1):
                tmp_thread = FuncThread(thread_count, self.spun_tlink_creator, source_topic,
                                        scored_desc_dict, rel_topics, topic_links)
                tmp_thread.start()
                threads.append(tmp_thread)
                print "Spun Topic_Link Creator Thread #", thread_count, "\n"
                thread_count += 1

            # wait for threads to return
            for t in threads:
                t.join()

            print "Exiting Main Thread...\n"
            sorted_tl = sorted(topic_links, key=lambda instance: instance.score, reverse=True)

            # added like this to prevent Index out of bounds error on sorted_tl
            num_linked_topics = DEFAULT_NUM_LINKED_TOPICS
            if len(sorted_tl) < num_linked_topics:
                all_linked_topics.extend(sorted_tl)
            else:
                all_linked_topics.extend(sorted_tl[0:num_linked_topics + 1])

            source_topic.linked_topics = all_linked_topics[0:6]
            source_topic.save()

        except Exception, E:
            print "Error: issue with threads"
            print str(E)

    def spun_topic_creator(self, rel_links, rel_topics, topic_desc_dict):
        topic_name = None
        exit_thread = False

        thread_lock1.acquire()
        if len(rel_links) == 0:
            exit_thread = True
        else:
            topic_name = rel_links.pop()
        thread_lock1.release()

        while not exit_thread and topic_name is not None:
            r_url = EXTRACT_URL.format(R_TITLE.format(topic_name))
            retrieve_flag = "extract"

            response = self.api_utils.make_api_request(r_url, EXCONT, retrieve_flag)
            linked_page = response[PAGE_RESP_KEY]
            redirected_page = response[REDIRECT_RESP_KEY] if REDIRECT_RESP_KEY in response else None

            linked_topic = self.api_utils.parse_and_save_topic(linked_page, redirected_page)[
                0]  # get the first element returned

            # add to topic_name -> description to dictionary
            thread_lock2.acquire()
            if linked_topic.article_id not in topic_desc_dict:
                rel_topics.append(linked_topic)
                topic_desc_dict.update({linked_topic.article_id: linked_topic.description})
            thread_lock2.release()

            thread_lock1.acquire()
            if len(rel_links) == 0:
                exit_thread = True
            else:
                topic_name = rel_links.pop()
            thread_lock1.release()

    def spun_tlink_creator(self, source_topic, scored_desc_dict, rel_topics, topic_links):
        linked_topic = None
        exit_thread = False

        thread_lock1.acquire()
        if len(rel_topics) == 0:
            exit_thread = True
        else:
            linked_topic = rel_topics.pop()
        thread_lock1.release()

        while not exit_thread and linked_topic is not None:
            # create topiclink relation for linked_topic
            rel_text = linked_topic.article_title + " is linked to " + source_topic.article_title
            tl_score = scored_desc_dict[linked_topic.article_id]
            tl_data = {"source_id": source_topic,
                       "target_id": linked_topic,
                       "title": linked_topic.article_title,
                       "description": rel_text,
                       "wiki_link": linked_topic.wiki_link,
                       "base_score": tl_score,
                       "user_score": 0.0,
                       "score": tl_score
                       }

            tlink = self.tl_creator.create_topiclink(tl_data)

            # add to topic_link to list of related topics
            thread_lock3.acquire()
            if tlink is not None:  # prevent creation of topiclink where source_id == target_id
                topic_links.append(tlink)
            thread_lock3.release()

            thread_lock1.acquire()
            if len(rel_topics) == 0:
                exit_thread = True
            else:
                linked_topic = rel_topics.pop()
            thread_lock1.release()


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


class FuncThread(threading.Thread):
    def __init__(self, thread_id, target, *args):
        self.thread_id = thread_id
        self._target = target
        self._args = args
        threading.Thread.__init__(self)

    def run(self):
        self._target(*self._args)
