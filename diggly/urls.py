from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt
from . import views

urlpatterns = [
    #ex: /diggly/
    url(r'^$', views.index, name='index'),
    
    #ex: /diggly/topics/
    url(r'^topics/$', views.list_topics, name='list_topics'),
    
    #ex: /diggly/topics/791/ 
    url(r'^topics/(?P<tid>[0-9]+)/$', views.get_topic_by_id, name='get_topic_by_id'),    

    #ex: /diggly/topics/related//all/791/ 
    url(r'^topics/related/all/(?P<tid>[0-9]+)/$', views.get_all_topiclinks, name='get_all_topiclinks'),

    #ex: /diggly/topics/related/top/791/ 
    url(r'^topics/related/top/(?P<tid>[0-9]+)/$', views.get_top_topiclinks, name='get_top_topiclinks'),

    #ex: /diggly/topics/explore/791/ 
    url(r'^topics/explore/(?P<tid>[0-9]+)/$', views.explore_topic, name='explore_topic'),

    #ex: /diggly/track/1234/<user/session-based token from cookie>
    url(r'^topics/track/$', csrf_exempt(views.track_topic), name='track_topic'),


    #ex: /diggly/topics/sections/related/791/ 
    #url(r'^topics/sections/(?P<tid>[0-9]+)/$', views.get_section_links, name='get_section_links'),
    
    #rest-framework browsable api
    #url(r'^api-auth/', 'rest_framework.urls', name='rest_framework'),

    #ex: /diggly/topics/solar_system/
    #TODO: uses '.*' to match any string
    #url(r'^topics/(?P<title>.*)/$', views.get_topic_title, name='view_topic'),
]
