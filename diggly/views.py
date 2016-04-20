import json
import random
import collections
from datetime import datetime, timedelta
from diggly.util.scoring.topic_score_update import update_score
from diggly.util.topic_visits.log_visit import log_visit
from diggly.util.serializers.topic_serializers import TopicSerializer, TopicLinkSerializer
from diggly.util.wikipediaAPI.wiki_api import WikipediaHelper
from django.forms.models import model_to_dict
from django.http import Http404
from django.http import HttpResponse
from django.db.models import Count, Max, Min
from models import Topic, TopicLink, TopicRedirect, TopicVisit
from rest_framework.renderers import JSONRenderer

from itertools import groupby

# 2015 wiki_diggly
# prototype v1

wiki_help = WikipediaHelper()
#jpedia_mgt = JsonPediaManager(description_len, summary_len)

def index(request):
    return HttpResponse("Hello! Welcome to the Diggly index.")

def list_topics(request):
    topics = Topic.objects.all()
    serializer = TopicSerializer(topics, many=True)
    return JSONResponse(serializer.data)

def explore_topic(request, tid):
    print "LOG: explore_topic; id  ->", tid
    topic = None
    
    try:
        print "[LOG] Retrieving data from MongoDB"
        topic = get_redirect_id(tid)
        
        if topic == None:
            topic = Topic.objects.get(article_id=tid)
        
        topiclinks = TopicLink.objects.filter(source_id=topic.article_id)

        topic.linked_topics = topiclinks[0:7]
        if len(topic.linked_topics) == 0:
            wiki_help.add_linked_topics(topic)

        data = json.dumps(topic.to_json())
        
    except Topic.DoesNotExist:
        print "[LOG] attempting to fetch data from wikipedia"
        topics = wiki_help.get_article(tid)
        topic = topics[0] 
        data = json.dumps(topic.to_json())

    log_visit(topic)
    return HttpResponse(data, content_type="application/json")        

def get_topic_by_id(request, tid):
    print "LOG: get_topic_title; tid ->", tid
    
    try:
        topic = get_redirect_id(tid)
        
        if topic == None:
            topic = Topic.objects.get(article_id=tid)

        serializer = TopicSerializer(topic)
        print "[LOG] retrieving topic request from MongoDB"   
 
    except Topic.DoesNotExist:
        raise Http404("Topic does not exist")
 
    return JSONResponse(serializer.data)


#helper method
#do not use in production
def get_all_topiclinks(request, tid):
    print "LOG: get_all_topiclinks; tid ->", tid

    try:
        topic = Topic.objects.get(article_id=tid)
        topiclinks = topic.topiclink_source.all()
        serializer = TopicLinkSerializer(topiclinks, many=True)
 
    except Topic.DoesNotExist:
        raise Http404("Topic does not exist")

    return JSONResponse(serializer.data)

def get_top_topiclinks(request, tid):
    print "LOG: get_all_topiclinks; tid ->", tid

    try:
        topic = Topic.objects.get(article_id=tid)
        topiclinks = topic.linked_topics
        serializer = TopicLinkSerializer(topiclinks, many=True)

    except Topic.DoesNotExist:
        raise Http404("Topic does not exist")
    
    return JSONResponse(serializer.data)

#user feedback is received
def track_topic(request):
    #print request, "\n"
    tid_src = request.POST.get('tid_src', '')
    tid_dst = request.POST.get('tid_dst', '')

    print "request-->", request, "\n"
    print "vals -->", tid_src, "\n", tid_dst, "\n"
    
    if(tid_src.strip() is '' or tid_dst.strip() is ''):
        return HttpResponse("Invalid Parameters")

    update_score(tid_src, tid_dst)
    response = "Done with request [{}:{}]\n"
    return HttpResponse(response.format(tid_src, tid_dst))

#get json for displaying on front-page for trending topic (within past week/7 days)
def get_homepage_trending(request):
    article_ids = [queryset.source_id.article_id for queryset in TopicVisit.objects.filter(visit_timestamp__gte=(datetime.now()-timedelta(days=7)))]
    print "article_ids --> ", article_ids, "\n"    
    counter=collections.Counter(article_ids)  # print counter, counter.values(), counter.keys()
    most_common_topic_id = str(counter.most_common(1)[0]) #convert tuple to string
    most_common_topic_id = most_common_topic_id.replace("(","").replace(")","").split(",") #sanitize and tokenize string
    most_common_topic_id = most_common_topic_id[0] #get first value (key)
    print(most_common_topic_id)
    topic = Topic.objects.get(article_id=most_common_topic_id)
    if topic:
        serializer = TopicSerializer(topic)
        return JSONResponse(serializer.data)
    else:
        raise Http404("No trending topics found")

#get json for displaying on front-page for popular topic (within past year/365 days)
def get_homepage_popular(request):
    article_ids = [queryset.source_id.article_id for queryset in TopicVisit.objects.filter(visit_timestamp__gte=(datetime.now()-timedelta(days=365)))]
    print "article_ids --> ", article_ids, "\n"    
    counter=collections.Counter(article_ids)  # print counter, counter.values(), counter.keys()
    most_common_topic_id = str(counter.most_common(1)[0]) #convert tuple to string
    most_common_topic_id = most_common_topic_id.replace("(","").replace(")","").split(",") #sanitize and tokenize string
    most_common_topic_id = most_common_topic_id[0] #get first value (key)
    print(most_common_topic_id)
    topic = Topic.objects.get(article_id=most_common_topic_id)
    if topic:
        serializer = TopicSerializer(topic)
        return JSONResponse(serializer.data)
    else:
        raise Http404("No popular topics found")

#get json for displaying on front-page for (3) most recently visited topics
def get_homepage_recent(request):        
    topic_visits = TopicVisit.objects.order_by('-visit_timestamp') #sort in desc order by date
    topic_visits = list(topic_visits)
    topics = list()
    if(topic_visits):
        for topic_visit in topic_visits:
            print topic_visit.source_id.article_id," : ", topic_visit.visit_timestamp,"\n"
            if (topic_visit.source_id not in topics) and len(topics)<3: #we don't want duplicate topics and no more than top 3 recent
                topics.append(topic_visit.source_id)
        serializer = TopicSerializer(topics, many=True)
        return JSONResponse(serializer.data)   
    else:
        raise Http404("No recent topics found")

#get json for displaying on front-page for (1) random topic
def get_homepage_random(request):  
    #send something random
    topic_visits = TopicVisit.objects.all()
    random_index = random.randint(0, TopicVisit.objects.count() - 1)
    random_topic_visit = topic_visits[random_index]
    serializer = TopicSerializer(random_topic_visit.source_id)
    return JSONResponse(serializer.data)

def convertTopicLink(topiclinks):
    res = []

    for tl in topiclinks:
        tmp = model_to_dict(tl)
        print "tmp ->", tmp
        res.append(model_to_dict(tl))

    res_sorted = sorted(res, key=lambda instance: instance.score, reverse=True)
    return res_sorted


#An HttpResponse that renders its content into JSON
class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
    
        #print data['linked_topics']   
     
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

#helper functions
def get_redirect_id(tid):
    print "LOG: get_redirect_id; tid ->", tid

    try:
        tl_redirect = TopicRedirect.objects.get(source_id=tid)
        return tl_redirect.redirect_topic

    except TopicRedirect.DoesNotExist:
        return None
