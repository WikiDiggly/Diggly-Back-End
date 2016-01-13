import json
from django.http import HttpResponse  
from django.core import serializers
from django.utils import simplejson
from itertools import chain

from models import Topic, TopicLink
from diggly_serializers import TopicSerializer, TopicLinkSerializer

from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser


# 2015 wiki_diggly
# author: ola-halima
# prototype v1

#An HttpResponse that renders its content into JSON
class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

def index(request):
    return HttpResponse("Hello! Welcome to the Diggly index.")

def list_topics(request):
    topics = Topic.objects.all()
    serializer = TopicSerializer(topics, many=True)
    return JSONResponse(serializer.data)

def explore_topic(request, tid):
    print "LOG: explore_topic; id  ->", tid

    try:
        topic = Topic.objects.get(article_id=tid)
        topiclist = topic.topiclink_source.all()
        sectionlist = topic.sectionlink_source.all()
       
        topic_data = json.dumps(topic.to_json())
 
        #combine topiclist and sectionlist, sort in ascending order by score
        all_rel = sorted(
                    chain(topiclist, sectionlist),
                    key=lambda instance: instance.score, reverse=True)

        #serialize data
        rel_data = serializers.serialize("json", all_rel, 
                fields=('article_id',
                        'article_title',
                        'summary',
                        'wiki_link',
                        'source_id', 
                        'target_id', 
                        'description', 
                        'redirect_article_id', 
                        'section_title', 
                        'main_article_id', 
                        'section_wiki_link', 
                        'score'))
    
        data = topic_data
        #data = simplejson.dumps([topic_data, rel_data])
        
    except Topic.DoesNotExist:
        raise Http404("Topic does not exist")

    #FIXME: is returning 2 json objects optimal?
    return HttpResponse(data, content_type="application/json")        

def get_topic_id(request, tid):
    print "LOG: get_topic_title; tid ->", tid
    
    try:
        topic = Topic.objects.get(article_id=tid)
        serializer = TopicSerializer(topic)
    
    except Topic.DoesNotExist:
        raise Http404("Topic does not exist")
    
    return JSONResponse(serializer.data)


#helper method
#do not use in production
def get_topic_links(request, tid):
    print "LOG: get_topic_links; tid ->", tid

    try:
        topic = Topic.objects.get(article_id=tid)
        topiclinks = topic.topiclink_source.all()
        serializer = TopicLinkSerializer(topiclinks, many=True)
 
    except Topic.DoesNotExist:
        raise Http404("Topic does not exist")

    return JSONResponse(serializer.data)

#helper method
#do not use in production
#def get_section_links(request, tid):
#    print "LOG: get_section_links; tid ->", tid

#    try:
#        topic = Topic.objects.get(article_id=tid) 
#        sectionlinks = topic.sectionlink_source.all()
#        serializer = SectionLinkSerializer(sectionlinks, many=True)
    
#    except Topic.DoesNotExist:
#        raise Http404("Topic does not exist")

#    return JSONResponse(serializer.data)            
