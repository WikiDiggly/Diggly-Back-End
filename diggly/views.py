import json
from django.http import HttpResponse  
from django.core import serializers
from django.utils import simplejson
from itertools import chain
from models import *

# 2015 wiki_diggly
# author: ola-halima
# prototype v1

def index(request):
    return HttpResponse("Hello! Welcome to the Diggly index.")

def list_topics(request):
    topics = Topic.objects.all()
    data = serializers.serialize("json", topics, 
            fields=('article_id', 
                    'article_title', 
                    'summary', 
                    'description', 
                    'wiki_link', 
                    'created', 
                    'modified')
    
)
    return HttpResponse(data)

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
    
        data = simplejson.dumps([topic_data, rel_data])
        
    except Topic.DoesNotExist:
        raise Http404("Topic does not exist")

    #FIXME: is returning 2 json objects optimal?
    return HttpResponse(data, content_type="application/json")        

def get_topic_id(request, tid):
    print "LOG: get_topic_title; tid ->", tid
    
    try:
        obj = Topic.objects.get(article_id=tid)
        data = json.dumps(obj.to_json())
    
    except Topic.DoesNotExist:
        raise Http404("Topic does not exist")
        
    return HttpResponse(data, content_type="application/json")


#helper method
#do not use in production
def get_topic_links(request, tid):
    print "LOG: get_topic_links; tid ->", tid

    try:
        print "LOG Attemptign to retrieve the topic now"
        topic = Topic.objects.get(article_id=tid)
        print "LOG The topic returned is:::::", topic
        topiclinks = topic.topiclink_source.all()
        data = serializers.serialize("json", topiclinks, 
                fields=('source_id', 
                        'target_id', 
                        'description', 
                        'score'))  
 
    except Topic.DoesNotExist:
        raise Http404("Topic does not exist")

    return HttpResponse(data, content_type="application/json")

#helper method
#do not use in production
def get_section_links(request, tid):
    print "LOG: get_section_links; tid ->", tid

    try:
        topic = Topic.objects.get(article_id=tid) 
        sectionlinks = topic.sectionlink_source.all()
        data = serializers.serialize("json", sectionlinks, 
                fields=('source_id',
                        'section_title', 
                        'main_article_id', 
                        'section_wiki_link', 
                        'score'))
    
    except Topic.DoesNotExist:
        raise Http404("Topic does not exist")

    return HttpResponse(data, content_type="application/json")            
