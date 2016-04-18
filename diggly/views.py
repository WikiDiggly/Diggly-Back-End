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
        
        if topic is None:
            topic = Topic.objects.get(article_id=tid)


        #topic_links = TopicLink.objects.filter(source_id=topic.article_id)
        #sorted_tl = sorted(topic_links, key=lambda instance: instance.score, reverse=True)
        #topic.linked_topics = sorted_tl[0:7]
        #topic.save()

        if len(topic.get_linked_topics()) == 0:
            wiki_help.update_article(topic)

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
        
        if topic is None:
            topic = Topic.objects.get(article_id=tid)

        serializer = TopicSerializer(topic)
        print "[LOG] retrieving topic request from MongoDB"   
 
    except Topic.DoesNotExist:
        raise Http404("Topic does not exist")
 
    return JSONResponse(serializer.data)


# helper method
# do not use in production
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

# user feedback is received
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


def convertTopicLink(topiclinks):
    res = []

    for tl in topiclinks:
        tmp = model_to_dict(tl)
        res.append(model_to_dict(tl))

    res_sorted = sorted(res, key=lambda instance: instance.score, reverse=True)
    return res_sorted


# an HttpResponse that renders its content into JSON
class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

# helper functions
def get_redirect_id(tid):
    print "LOG: get_redirect_id; tid ->", tid

    try:
        tl_redirect = TopicRedirect.objects.get(source_id=tid)
        return tl_redirect.redirect_topic

    except TopicRedirect.DoesNotExist:
        return None
