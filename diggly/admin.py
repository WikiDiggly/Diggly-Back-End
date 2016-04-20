from django.contrib import admin
from django.contrib.admin import site, ModelAdmin
from .models import Topic, TopicLink, TopicRedirect, TopicVisit


#def linked_topics(instance):
#    return ', '.join(instance.linked_topics)

#class TopicAdmin(ModelAdmin):
#    list_display = ['target_id', linked_topics]

admin.site.register(Topic)
admin.site.register(TopicLink)
admin.site.register(TopicRedirect)
admin.site.register(TopicVisit)