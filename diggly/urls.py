from django.conf.urls import url
from . import views

urlpatterns = [
    #ex: /diggly/
    url(r'^$', views.index, name='index'),

    #rest-framework browsable api
    url(r'^api-auth/', 'rest_framework.urls', name='rest_framework'),
    
    #ex: /diggly/topics/
    url(r'^topics/$', views.list_topics, name='list_topics'),
    
    #ex: /diggly/topics/791/ 
    url(r'^topics/(?P<tid>[0-9]+)/$', views.get_topic_id, name='get_topic'),    

    #ex: /diggly/topics/related/791/ 
    url(r'^topics/related/(?P<tid>[0-9]+)/$', views.get_topic_links, name='get_topic_links'),

    #ex: /diggly/topics/sections/related/791/ 
    #url(r'^topics/sections/(?P<tid>[0-9]+)/$', views.get_section_links, name='get_section_links'),

    #ex: /diggly/topics/sections/related/791/ 
    url(r'^topics/explore/(?P<tid>[0-9]+)/$', views.explore_topic, name='explore_topic'),

    #ex: /diggly/topics/solar_system/
    #TODO: uses '.*' to match any string
    #url(r'^topics/(?P<title>.*)/$', views.get_topic_title, name='view_topic'),
]
