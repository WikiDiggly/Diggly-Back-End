import json
from diggly.util.scoring.topic_score_update import update_score
from diggly.util.serializers.topic_serializers import TopicSerializer, TopicLinkSerializer
from diggly.util.wikipediaAPI.wiki_api import WikipediaHelper
from django.forms.models import model_to_dict
from django.http import Http404
from django.http import HttpResponse
from models import Topic, TopicLink, TopicRedirect
from rest_framework.renderers import JSONRenderer

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

    try:
        print "[LOG] Retrieving data from MongoDB"
        topic = get_redirect_id(tid)
        
        if topic == None:
            topic = Topic.objects.get(article_id=tid)
        
        topiclinks = TopicLink.objects.filter(source_id=topic.article_id)

        topic.linked_topics = topiclinks[0:7]
        if len(topic.linked_topics) == 0:
            wiki_help.add_linked_topics(topic, None)

        data = json.dumps(topic.to_json())
        
    except Topic.DoesNotExist:
        print "[LOG] attempting to fetch data from wikipedia"
        topics = wiki_help.get_article(tid)
        topic = topics[0] 
        data = json.dumps(topic.to_json())

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
def track_topic(request, tid_src, tid_dst):
    print request, "\n", tid_src, "\n", tid_dst, "\n"
    update_score(tid_src, tid_dst)

    return HttpResponse('Done with request')
    



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
