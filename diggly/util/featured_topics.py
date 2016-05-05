from datetime import datetime, timedelta
from diggly.util.diggly_threads import FuncThread
from django.db.models import Max, Q
from diggly.models import Topic, FeaturedTopics, TopicRedirect
from diggly.util.wikipediaAPI.wiki_api import WikipediaHelper
from bs4 import BeautifulSoup
import requests

#constants; to be moved to another file
TRENDING_TOPICS_URL = "http://wikipedia.trending.eu/en/__[404]24/"
TRENDING_TOPICS_BACKUP_URL = "http://tools.wmflabs.org/wikitrends/english-most-visited-today.html"

GET_PAGE_ID_URL = "http://rack36.cs.drexel.edu/getpageid/?q="

wiki_help = WikipediaHelper()

def update_featured_object(topic):
    #Get featured topics instance
    featured_topics = None
    now = datetime.now()
    earlier_recent = timedelta(hours=1) #within last 1 hour (applies to recent topics)
    earlier_trending = timedelta(days=1) #within last 1 day (applies to trending topics)

    topic.visit_counter += 1
    topic.save()

    try:
        featured_topics = FeaturedTopics.objects.all()[0]
        recent_topics = featured_topics.recent_topics

        #Update recent topics object once an hour while ensuring all objects are unique
        if topic not in recent_topics and featured_topics.recent_topic_timestamp < (now-earlier_recent):
            while len(recent_topics) >= 3:
                recent_topics.pop(0)
            recent_topics.append(topic)
            featured_topics.recent_topics = recent_topics
            featured_topics.recent_topic_timestamp = now

        max_visit_counter = Topic.objects.aggregate(Max('visit_counter'))['visit_counter__max']
        new_popular_topic = Topic.objects.filter(visit_counter=max_visit_counter)[0]

        if featured_topics.popular_topic.article_id != new_popular_topic.article_id:
            featured_topics.popular_topic = new_popular_topic

        #trending topics
        if featured_topics.trending_topics_timestamp < (now-earlier_trending):
            featured_topics.trending_topics = get_trending_topics() 
            featured_topics.trending_topics_timestamp = now

    except IndexError:
        featured_topics = FeaturedTopics()
        random_topics = Topic.objects.filter(~Q(article_id=topic.article_id))[:2]
        featured_topics.recent_topics = [random_topics[0], random_topics[1], topic]
        featured_topics.recent_topic_timestamp = now

        max_visit_counter = Topic.objects.aggregate(Max('visit_counter'))['visit_counter__max']
        new_popular_topic = Topic.objects.filter(visit_counter=max_visit_counter)[0]
        featured_topics.trending_topics = get_trending_topics()
        featured_topics.recent_topic_timestamp = now 

    featured_topics.save()

def get_trending_topics():
    resp = requests.get(TRENDING_TOPICS_URL)
    if(resp.status_code != 200):
        print "Using backup source ...", "\n"
        resp = requests.get(TRENDING_TOPICS_BACKUP_URL)

    soup = BeautifulSoup(resp.text, "html.parser")
    anchors = soup.findAll('a')
    trending_topics = []
    for a in anchors:
        link = a['href']
        if(len(trending_topics) >= 10):
            break
        if ("http://en.wikipedia.org/" in link) or ("https://en.wikipedia.org/" in link):
            page_title = link.replace("http://en.wikipedia.org/wiki/", "").replace("https://en.wikipedia.org/wiki/", "").strip() #sanitize string
            resp2 = requests.get(GET_PAGE_ID_URL + page_title)
            resp2_json = resp2.json()
            page_id = resp2_json['pageid']
            print "Adding page ID: ", page_id, "\n"
            topic = None
            try:
                print "[LOG] Retrieving data from MongoDB"
                topic = get_redirect_id(page_id)
                
                if topic is None:
                    topic = Topic.objects.get(article_id=page_id)

                if len(topic.get_linked_topics()) == 0:
                    wiki_help.update_article(topic)
            
            except Topic.DoesNotExist:
                print "[LOG] attempting to fetch data from wikipedia"
                topics_wikipedia = wiki_help.get_article(page_id)
                topic = topics_wikipedia[0]
            print "topic ID  from object => ", topic.article_id, "\n"
            trending_topics.append(topic)

    return trending_topics

def get_redirect_id(tid):
    print "LOG: get_redirect_id; tid ->", tid

    try:
        tl_redirect = TopicRedirect.objects.get(source_id=tid)
        return tl_redirect.redirect_topic

    except TopicRedirect.DoesNotExist:
        return None